/**
 * Network Application - Frontend Architecture & Interactive Engine
 * CS50 Web Programming Project 4
 */

document.addEventListener("DOMContentLoaded", () => {
    initializeApp();
});

/**
 * Initializes all event listeners and component logic.
 */
function initializeApp() {
    setupCharacterCounter();
    setupCreatePostForm();
    setupFollowButton();
    setupEventDelegation();
}

/**
 * Gets the CSRF token from hidden input or cookie.
 */
function getCsrfToken() {
    const input = document.getElementById("global-csrf-token");
    if (input && input.value) {
        return input.value;
    }
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Shows Bootstrap Toast Notification.
 */
function showToast(message, isError = false) {
    const toastElement = document.getElementById("liveToast");
    const toastMessage = document.getElementById("toastMessage");

    if (!toastElement || !toastMessage) return;

    if (isError) {
        toastMessage.innerHTML = `<i class="bi bi-exclamation-triangle-fill text-danger fs-5"></i> <span>${message}</span>`;
    } else {
        toastMessage.innerHTML = `<i class="bi bi-check-circle-fill text-success fs-5"></i> <span>${message}</span>`;
    }

    const toast = new bootstrap.Toast(toastElement, { delay: 3500 });
    toast.show();
}

/**
 * Character counter for the composer textarea.
 */
function setupCharacterCounter() {
    const textarea = document.getElementById("post-content");
    const counter = document.getElementById("char-counter");

    if (!textarea || !counter) return;

    textarea.addEventListener("input", () => {
        const length = textarea.value.length;
        counter.textContent = length;

        if (length >= 260) {
            counter.className = "fw-bold text-danger";
        } else if (length >= 220) {
            counter.className = "fw-semibold text-warning";
        } else {
            counter.className = "fw-semibold text-secondary";
        }
    });
}

/**
 * Handles asynchronous post creation without page reload.
 */
function setupCreatePostForm() {
    const form = document.getElementById("create-post-form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const textarea = document.getElementById("post-content");
        const submitBtn = document.getElementById("post-submit-btn");
        const postsContainer = document.getElementById("posts-container");
        const content = textarea.value.trim();

        if (!content) {
            showToast("Post content cannot be empty.", true);
            return;
        }

        // Disable submit button during request
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> Posting...`;

        try {
            const response = await fetch("/api/posts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                },
                body: JSON.stringify({ content })
            });

            const data = await response.json();

            if (response.ok && data.post) {
                // Clear textarea and reset counter
                textarea.value = "";
                const counter = document.getElementById("char-counter");
                if (counter) counter.textContent = "0";

                // Remove empty state if present
                const emptyState = postsContainer.querySelector(".py-5");
                if (emptyState) {
                    emptyState.remove();
                }

                // Render and prepend new post card
                const newPostCardHtml = renderPostCardHtml(data.post);
                postsContainer.insertAdjacentHTML("afterbegin", newPostCardHtml);

                showToast("Post published successfully!");
            } else {
                showToast(data.error || "Failed to create post.", true);
            }
        } catch (error) {
            console.error("Create post error:", error);
            showToast("An error occurred while creating your post.", true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>Post</span> <i class="bi bi-send-fill fs-6"></i>`;
        }
    });
}

/**
 * Handles asynchronous follow/unfollow toggle.
 */
function setupFollowButton() {
    const followBtn = document.getElementById("follow-btn");
    if (!followBtn) return;

    followBtn.addEventListener("click", async () => {
        const username = followBtn.dataset.username;
        const followersCountElem = document.getElementById("followers-count");

        followBtn.disabled = true;

        try {
            const response = await fetch(`/api/users/${encodeURIComponent(username)}/follow`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                }
            });

            const data = await response.json();

            if (response.ok) {
                if (data.following) {
                    followBtn.className = "btn btn-outline-danger rounded-pill px-4 fw-semibold shadow-sm transition-all";
                    followBtn.innerHTML = `<i class="bi bi-person-dash-fill me-1"></i> Unfollow`;
                    showToast(`You are now following ${username}.`);
                } else {
                    followBtn.className = "btn btn-primary rounded-pill px-4 fw-semibold shadow-sm transition-all";
                    followBtn.innerHTML = `<i class="bi bi-person-plus-fill me-1"></i> Follow`;
                    showToast(`You unfollowed ${username}.`);
                }

                if (followersCountElem && data.followers_count !== undefined) {
                    followersCountElem.textContent = data.followers_count;
                }
            } else {
                showToast(data.error || "Failed to update follow status.", true);
            }
        } catch (error) {
            console.error("Follow toggle error:", error);
            showToast("An error occurred. Please try again.", true);
        } finally {
            followBtn.disabled = false;
        }
    });
}

/**
 * Event delegation for dynamically rendered posts (Likes, Edit, Save, Cancel).
 */
function setupEventDelegation() {
    const postsContainer = document.getElementById("posts-container");
    if (!postsContainer) return;

    postsContainer.addEventListener("click", async (event) => {
        const target = event.target;

        // 1. Like / Unlike Toggle Button
        const likeBtn = target.closest(".like-btn");
        if (likeBtn) {
            event.preventDefault();
            handleLikeToggle(likeBtn);
            return;
        }

        // 2. Edit Post Button
        const editBtn = target.closest(".edit-post-btn");
        if (editBtn) {
            const postId = editBtn.dataset.postId;
            toggleEditMode(postId, true);
            return;
        }

        // 3. Cancel Edit Button
        const cancelBtn = target.closest(".cancel-edit-btn");
        if (cancelBtn) {
            const postId = cancelBtn.dataset.postId;
            toggleEditMode(postId, false);
            return;
        }

        // 4. Save Edit Button
        const saveBtn = target.closest(".save-edit-btn");
        if (saveBtn) {
            const postId = saveBtn.dataset.postId;
            handleSaveEdit(postId, saveBtn);
            return;
        }
    });
}

/**
 * Toggles post card between view mode and edit mode.
 */
function toggleEditMode(postId, showEdit) {
    const contentBody = document.getElementById(`post-content-${postId}`);
    const editContainer = document.getElementById(`post-edit-${postId}`);

    if (!contentBody || !editContainer) return;

    if (showEdit) {
        contentBody.classList.add("d-none");
        editContainer.classList.remove("d-none");
        const textarea = editContainer.querySelector(".edit-textarea");
        if (textarea) {
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
    } else {
        editContainer.classList.add("d-none");
        contentBody.classList.remove("d-none");
    }
}

/**
 * Asynchronously saves post content edits.
 */
async function handleSaveEdit(postId, saveBtn) {
    const editContainer = document.getElementById(`post-edit-${postId}`);
    const contentBody = document.getElementById(`post-content-${postId}`);
    if (!editContainer || !contentBody) return;

    const textarea = editContainer.querySelector(".edit-textarea");
    const newContent = textarea.value.trim();

    if (!newContent) {
        showToast("Post content cannot be empty.", true);
        return;
    }

    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";

    try {
        const response = await fetch(`/api/posts/${postId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify({ content: newContent })
        });

        const data = await response.json();

        if (response.ok && data.post) {
            // Escape HTML and format linebreaks for rendered view
            contentBody.innerHTML = escapeHtml(data.post.content).replace(/\n/g, "<br>");
            toggleEditMode(postId, false);
            showToast("Post updated successfully!");
        } else {
            showToast(data.error || "Failed to update post.", true);
        }
    } catch (error) {
        console.error("Save post edit error:", error);
        showToast("An error occurred while saving changes.", true);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Changes";
    }
}

/**
 * Asynchronously toggles like status for a post.
 */
async function handleLikeToggle(likeBtn) {
    const postId = likeBtn.dataset.postId;
    const countSpan = document.getElementById(`like-count-${postId}`);
    const icon = likeBtn.querySelector(".like-icon");

    if (!postId || likeBtn.disabled) return;

    try {
        const response = await fetch(`/api/posts/${postId}/like`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken()
            }
        });

        const data = await response.json();

        if (response.ok) {
            if (data.liked) {
                likeBtn.classList.add("liked", "text-danger");
                likeBtn.classList.remove("text-secondary");
                if (icon) {
                    icon.classList.remove("bi-heart");
                    icon.classList.add("bi-heart-fill");
                }
            } else {
                likeBtn.classList.remove("liked", "text-danger");
                likeBtn.classList.add("text-secondary");
                if (icon) {
                    icon.classList.remove("bi-heart-fill");
                    icon.classList.add("bi-heart");
                }
            }

            if (countSpan && data.likes_count !== undefined) {
                countSpan.textContent = data.likes_count;
            }
        } else {
            showToast(data.error || "Could not toggle like.", true);
        }
    } catch (error) {
        console.error("Like toggle error:", error);
        showToast("An error occurred while updating like.", true);
    }
}

/**
 * Generates HTML string for a new post card.
 */
function renderPostCardHtml(post) {
    const initial = post.user ? post.user.charAt(0).toUpperCase() : "?";
    const editBtnHtml = post.is_owner ? `
        <button class="btn btn-link text-secondary p-1 rounded-circle hover-bg edit-post-btn" data-post-id="${post.id}" title="Edit Post">
            <i class="bi bi-pencil-square fs-5"></i>
        </button>
    ` : "";

    const formattedContent = escapeHtml(post.content).replace(/\n/g, "<br>");

    return `
        <div class="card border-0 shadow-sm rounded-4 post-card transition-all" data-post-id="${post.id}">
            <div class="card-body p-3 p-sm-4">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center gap-3">
                        <a href="/profile/${encodeURIComponent(post.user)}" class="text-decoration-none">
                            <div class="avatar-md bg-gradient text-white rounded-circle fw-bold d-flex align-items-center justify-content-center shadow-sm">
                                ${initial}
                            </div>
                        </a>
                        <div>
                            <a href="/profile/${encodeURIComponent(post.user)}" class="fw-bold text-dark text-decoration-none hover-underline fs-6">
                                ${escapeHtml(post.user)}
                            </a>
                            <div class="text-muted small d-flex align-items-center gap-1">
                                <i class="bi bi-calendar3"></i>
                                <span>${post.timestamp}</span>
                            </div>
                        </div>
                    </div>
                    ${editBtnHtml}
                </div>

                <!-- Post Content Body -->
                <div class="post-content-body fs-6 text-dark my-3" id="post-content-${post.id}">
                    ${formattedContent}
                </div>

                <!-- Hidden Edit Container -->
                <div class="post-edit-container d-none my-3" id="post-edit-${post.id}">
                    <textarea class="form-control border rounded-3 p-3 edit-textarea mb-2" rows="3">${escapeHtml(post.content)}</textarea>
                    <div class="d-flex gap-2 justify-content-end">
                        <button class="btn btn-outline-secondary btn-sm rounded-pill px-3 cancel-edit-btn" data-post-id="${post.id}">Cancel</button>
                        <button class="btn btn-primary btn-sm rounded-pill px-3 save-edit-btn" data-post-id="${post.id}">Save Changes</button>
                    </div>
                </div>

                <!-- Card Action Footer -->
                <div class="d-flex align-items-center justify-content-between border-top pt-3 mt-2 text-muted">
                    <button class="btn btn-link p-0 text-decoration-none d-flex align-items-center gap-2 like-btn ${post.is_liked ? 'liked text-danger' : 'text-secondary'}" data-post-id="${post.id}">
                        <i class="bi ${post.is_liked ? 'bi-heart-fill' : 'bi-heart'} fs-5 like-icon"></i>
                        <span class="fw-semibold like-count" id="like-count-${post.id}">${post.likes_count}</span>
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Escapes HTML characters to prevent XSS.
 */
function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
