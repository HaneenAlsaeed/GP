/**
 * AI Decision Hub - Interactive Frontend JavaScript Engine
 * CS50 Web Programming Final Project
 */

document.addEventListener("DOMContentLoaded", () => {
    initializeApp();
});

/**
 * Initializes all event handlers and dynamic features.
 */
function initializeApp() {
    setupLiveSearchAndFilters();
    setupFavoriteToggle();
    setupCommentForm();
}

/**
 * Helper to retrieve CSRF token.
 */
function getCsrfToken() {
    const input = document.getElementById("global-csrf-token");
    if (input && input.value) return input.value;

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
 * Helper to display Bootstrap Toast alerts.
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
 * Live search and multi-parameter filtering without page reloads.
 */
function setupLiveSearchAndFilters() {
    const searchInput = document.getElementById("live-search-input");
    const filterSelects = document.querySelectorAll(".filter-select");
    const gridContainer = document.getElementById("decisions-grid");

    if (!gridContainer) return;

    let debounceTimer = null;

    const executeFilter = async () => {
        const projectId = searchInput ? searchInput.dataset.projectId : null;
        const q = searchInput ? searchInput.value.trim() : "";
        const risk = document.getElementById("filter-risk") ? document.getElementById("filter-risk").value : "";
        const priority = document.getElementById("filter-priority") ? document.getElementById("filter-priority").value : "";
        const status = document.getElementById("filter-status") ? document.getElementById("filter-status").value : "";
        const category = document.getElementById("filter-category") ? document.getElementById("filter-category").value : "";

        let url = `/api/decisions/?q=${encodeURIComponent(q)}&risk=${encodeURIComponent(risk)}&priority=${encodeURIComponent(priority)}&status=${encodeURIComponent(status)}&category=${encodeURIComponent(category)}`;
        if (projectId) {
            url += `&project_id=${projectId}`;
        }

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (response.ok && data.decisions) {
                renderDecisionsGrid(data.decisions, gridContainer);
            }
        } catch (error) {
            console.error("Filter request error:", error);
        }
    };

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(executeFilter, 300);
        });
    }

    filterSelects.forEach(select => {
        select.addEventListener("change", executeFilter);
    });
}

/**
 * Re-renders the decisions grid dynamically.
 */
function renderDecisionsGrid(decisions, container) {
    if (decisions.length === 0) {
        container.innerHTML = `
            <div class="col-12" id="no-decisions-empty-state">
                <div class="card border-0 shadow-sm rounded-4 py-5 text-center bg-white my-3">
                    <div class="card-body">
                        <i class="bi bi-search display-3 text-secondary opacity-50 mb-3"></i>
                        <h5 class="fw-bold text-dark">No decisions match your filters</h5>
                        <p class="text-secondary mb-0">Try adjusting your search terms or filter selections.</p>
                    </div>
                </div>
            </div>
        `;
        return;
    }

    const cardsHtml = decisions.map(d => {
        let riskBadgeClass = "bg-success";
        if (d.risk_level === "CRITICAL") riskBadgeClass = "bg-danger";
        else if (d.risk_level === "HIGH") riskBadgeClass = "bg-warning text-dark";
        else if (d.risk_level === "MEDIUM") riskBadgeClass = "bg-info text-dark";

        return `
            <div class="col-12 col-md-6 col-xl-4 decision-card-col" data-decision-id="${d.id}">
                <div class="card border-0 shadow-sm rounded-4 h-100 decision-card bg-white transition-all">
                    <div class="card-body p-4 d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge bg-${d.category_color}-subtle text-${d.category_color} rounded-pill px-3 py-1.5 fw-semibold small">
                                <i class="bi ${d.category_icon} me-1"></i> ${escapeHtml(d.category)}
                            </span>
                            <button class="btn btn-link text-warning p-0 star-favorite-btn" data-decision-id="${d.id}" title="Star Decision">
                                <i class="bi ${d.is_favorite ? 'bi-star-fill' : 'bi-star'} fs-5 star-icon"></i>
                            </button>
                        </div>

                        <h5 class="fw-bold text-dark mb-2 mt-1">${escapeHtml(d.title)}</h5>
                        <p class="text-secondary small flex-grow-1 mb-3">${escapeHtml(truncateWords(d.description, 18))}</p>

                        <div class="d-flex align-items-center gap-2 mb-3">
                            <span class="badge ${riskBadgeClass} rounded-pill px-2.5 py-1">${escapeHtml(d.risk_display)}</span>
                            <span class="badge bg-light text-secondary border rounded-pill px-2.5 py-1">${escapeHtml(d.priority_display)}</span>
                            <span class="badge bg-primary-subtle text-primary rounded-pill px-2.5 py-1 ms-auto">${escapeHtml(d.status_display)}</span>
                        </div>

                        <div class="border-top pt-3 d-flex justify-content-between align-items-center mt-auto text-secondary small">
                            <div class="d-flex gap-3">
                                <span><i class="bi bi-chat-left-text me-1"></i>${d.comments_count}</span>
                                <span><i class="bi bi-paperclip me-1"></i>${d.attachments_count}</span>
                            </div>
                            <a href="/decisions/${d.id}/" class="btn btn-outline-primary btn-sm rounded-pill px-3">
                                Analyze & Open <i class="bi bi-chevron-right ms-1"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join("");

    container.innerHTML = cardsHtml;
}

/**
 * Handles Star / Unstar favorite toggling asynchronously.
 */
function setupFavoriteToggle() {
    document.addEventListener("click", async (event) => {
        const starBtn = event.target.closest(".star-favorite-btn");
        if (!starBtn) return;

        event.preventDefault();
        const decisionId = starBtn.dataset.decisionId;
        const icon = starBtn.querySelector(".star-icon");

        try {
            const response = await fetch(`/api/decisions/${decisionId}/favorite/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                }
            });

            const data = await response.json();

            if (response.ok) {
                if (data.is_favorite) {
                    if (icon) {
                        icon.classList.remove("bi-star");
                        icon.classList.add("bi-star-fill");
                    }
                    showToast("Starred decision added to favorites!");
                } else {
                    if (icon) {
                        icon.classList.remove("bi-star-fill");
                        icon.classList.add("bi-star");
                    }
                    showToast("Decision removed from favorites.");
                }
            } else {
                showToast(data.error || "Failed to toggle favorite.", true);
            }
        } catch (error) {
            console.error("Favorite toggle error:", error);
            showToast("An error occurred. Please try again.", true);
        }
    });
}

/**
 * Handles async comment submission.
 */
function setupCommentForm() {
    const commentForm = document.getElementById("add-comment-form");
    if (!commentForm) return;

    commentForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const decisionId = commentForm.dataset.decisionId;
        const textarea = document.getElementById("comment-text");
        const submitBtn = document.getElementById("comment-submit-btn");
        const streamContainer = document.getElementById("comments-stream-container");
        const text = textarea.value.trim();

        if (!text) {
            showToast("Comment text cannot be empty.", true);
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = "Posting...";

        try {
            const response = await fetch(`/api/decisions/${decisionId}/comment/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken()
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (response.ok && data.comment) {
                textarea.value = "";

                // Remove empty state if present
                const emptyState = document.getElementById("no-comments-empty");
                if (emptyState) emptyState.remove();

                // Render and prepend comment
                const newCommentHtml = `
                    <div class="comment-item bg-light rounded-3 p-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <div class="d-flex align-items-center gap-2">
                                <div class="avatar-sm bg-primary text-white rounded-circle fw-bold d-flex align-items-center justify-content-center">
                                    ${data.comment.author_initial}
                                </div>
                                <span class="fw-bold text-dark small">${escapeHtml(data.comment.author)}</span>
                            </div>
                            <span class="text-secondary small" style="font-size: 0.75rem;">${data.comment.timestamp}</span>
                        </div>
                        <p class="text-dark mb-0 small ms-4 ps-2">${escapeHtml(data.comment.text).replace(/\n/g, '<br>')}</p>
                    </div>
                `;

                streamContainer.insertAdjacentHTML("afterbegin", newCommentHtml);
                showToast("Comment posted successfully!");
            } else {
                showToast(data.error || "Failed to post comment.", true);
            }
        } catch (error) {
            console.error("Post comment error:", error);
            showToast("An error occurred while posting comment.", true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Post Note";
        }
    });
}

/**
 * HTML Escaper helper.
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

/**
 * Truncate words helper.
 */
function truncateWords(str, numWords) {
    if (!str) return "";
    const words = str.split(/\s+/);
    if (words.length <= numWords) return str;
    return words.slice(0, numWords).join(" ") + "...";
}
