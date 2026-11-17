/**
 * CustomerHub dashboard interactions.
 * Progressive enhancement over server-rendered pages: sidebar, modals,
 * profile drawer, toasts, live search, and client-side form validation.
 * Every action degrades to plain navigation when JavaScript is unavailable.
 */
(function () {
    "use strict";

    var PENDING_TOAST_KEY = "ch-toast";
    var SIDEBAR_KEY = "ch-sidebar-collapsed";

    /* ---------- Utilities ---------- */

    function $(selector, root) {
        return (root || document).querySelector(selector);
    }

    function csrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    function escapeHtml(value) {
        return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
        });
    }

    function formatDate(value) {
        var match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value || "");
        if (!match) return value || "—";
        var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return months[parseInt(match[2], 10) - 1] + " " + parseInt(match[3], 10) + ", " + match[1];
    }

    function initials(firstName, lastName) {
        return ((firstName || "?").charAt(0) + (lastName || "").charAt(0)).toUpperCase();
    }

    /* ---------- Toasts ---------- */

    function toastContainer() {
        return document.getElementById("toast-container");
    }

    function dismissToast(toast) {
        toast.classList.remove("show");
        window.setTimeout(function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 300);
    }

    function showToast(message, type) {
        var container = toastContainer();
        if (!container) return;
        var toast = document.createElement("div");
        toast.className = "toast toast-" + (type === "error" ? "error" : "success");
        toast.setAttribute("role", type === "error" ? "alert" : "status");
        var text = document.createElement("span");
        text.className = "toast-message";
        text.textContent = message;
        var close = document.createElement("button");
        close.type = "button";
        close.className = "toast-close";
        close.setAttribute("aria-label", "Dismiss notification");
        close.textContent = "×";
        close.addEventListener("click", function () { dismissToast(toast); });
        toast.appendChild(text);
        toast.appendChild(close);
        container.appendChild(toast);
        requestAnimationFrame(function () { toast.classList.add("show"); });
        if (type !== "error") {
            window.setTimeout(function () { dismissToast(toast); }, 5000);
        }
    }

    function queueToastAfterReload(message, type) {
        try {
            window.sessionStorage.setItem(PENDING_TOAST_KEY, JSON.stringify({ message: message, type: type }));
        } catch (err) { /* storage unavailable; skip queued toast */ }
    }

    function enhanceServerToasts() {
        var toasts = document.querySelectorAll("[data-toast]");
        toasts.forEach(function (toast) {
            requestAnimationFrame(function () { toast.classList.add("show"); });
            var close = toast.querySelector(".toast-close");
            if (close) close.addEventListener("click", function () { dismissToast(toast); });
            if (!toast.classList.contains("toast-error")) {
                window.setTimeout(function () { dismissToast(toast); }, 5000);
            }
        });
    }

    function showPendingToast() {
        var raw = null;
        try {
            raw = window.sessionStorage.getItem(PENDING_TOAST_KEY);
            window.sessionStorage.removeItem(PENDING_TOAST_KEY);
        } catch (err) { return; }
        if (!raw) return;
        try {
            var pending = JSON.parse(raw);
            if (pending && pending.message) showToast(pending.message, pending.type || "success");
        } catch (err) { /* ignore malformed payload */ }
    }

    /* ---------- Sidebar ---------- */

    function initSidebar() {
        try {
            if (window.localStorage.getItem(SIDEBAR_KEY) === "1") {
                document.body.classList.add("sidebar-collapsed");
            }
        } catch (err) { /* ignore */ }

        var collapse = document.getElementById("sidebar-collapse");
        if (collapse) {
            collapse.addEventListener("click", function () {
                var collapsed = document.body.classList.toggle("sidebar-collapsed");
                collapse.setAttribute("aria-expanded", collapsed ? "false" : "true");
                try {
                    window.localStorage.setItem(SIDEBAR_KEY, collapsed ? "1" : "0");
                } catch (err) { /* ignore */ }
            });
        }

        var menu = document.getElementById("topbar-menu");
        var overlay = document.getElementById("sidebar-overlay");
        if (menu) {
            menu.addEventListener("click", function () {
                var open = document.body.classList.toggle("sidebar-open");
                menu.setAttribute("aria-expanded", open ? "true" : "false");
            });
        }
        if (overlay) {
            overlay.addEventListener("click", function () {
                document.body.classList.remove("sidebar-open");
                if (menu) menu.setAttribute("aria-expanded", "false");
            });
        }
    }

    /* ---------- Row action menus ---------- */

    function closeAllMenus(except) {
        document.querySelectorAll("details.row-menu[open]").forEach(function (menu) {
            if (menu !== except) menu.removeAttribute("open");
        });
    }

    function initMenus() {
        document.addEventListener("toggle", function (event) {
            var menu = event.target;
            if (menu && menu.classList && menu.classList.contains("row-menu") && menu.open) {
                closeAllMenus(menu);
            }
        }, true);
        document.addEventListener("click", function (event) {
            if (!event.target.closest("details.row-menu")) closeAllMenus(null);
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeAllMenus(null);
        });
    }

    /* ---------- Modal ---------- */

    var lastFocused = null;

    function modalRoot() {
        return document.getElementById("modal-root");
    }

    function openModal(options) {
        closeModal();
        lastFocused = document.activeElement;
        var root = modalRoot();
        if (!root) return null;

        var overlay = document.createElement("div");
        overlay.className = "modal-overlay";
        overlay.setAttribute("role", "presentation");
        var dialog = document.createElement("div");
        dialog.className = "modal" + (options.size === "sm" ? " modal-sm" : "");
        dialog.setAttribute("role", "dialog");
        dialog.setAttribute("aria-modal", "true");
        dialog.setAttribute("aria-label", options.title || "Dialog");

        var header = document.createElement("div");
        header.className = "modal-header";
        var heading = document.createElement("div");
        var title = document.createElement("h2");
        title.className = "modal-title";
        title.textContent = options.title || "";
        heading.appendChild(title);
        if (options.subtitle) {
            var sub = document.createElement("p");
            sub.className = "modal-subtitle";
            sub.textContent = options.subtitle;
            heading.appendChild(sub);
        }
        var closeBtn = document.createElement("button");
        closeBtn.type = "button";
        closeBtn.className = "modal-close";
        closeBtn.setAttribute("aria-label", "Close dialog");
        closeBtn.textContent = "×";
        closeBtn.addEventListener("click", closeModal);
        header.appendChild(heading);
        header.appendChild(closeBtn);

        var body = document.createElement("div");
        body.className = "modal-body";
        if (typeof options.body === "string") {
            body.innerHTML = options.body;
        } else if (options.body) {
            body.appendChild(options.body);
        } else {
            body.innerHTML = '<p class="modal-loading">Loading…</p>';
        }

        dialog.appendChild(header);
        dialog.appendChild(body);
        overlay.appendChild(dialog);
        root.appendChild(overlay);
        overlay.addEventListener("mousedown", function (event) {
            if (event.target === overlay) closeModal();
        });
        requestAnimationFrame(function () { overlay.classList.add("open"); });
        closeBtn.focus();
        return body;
    }

    function closeModal() {
        var root = modalRoot();
        if (root) root.innerHTML = "";
        if (lastFocused && document.contains(lastFocused)) lastFocused.focus();
        lastFocused = null;
    }

    function setModalBody(html) {
        var body = modalRoot() ? modalRoot().querySelector(".modal-body") : null;
        if (body) body.innerHTML = html;
        return body;
    }

    function openFormModal(url, title, subtitle) {
        var body = openModal({ title: title, subtitle: subtitle });
        if (!body) {
            window.location.href = url;
            return;
        }
        fetch(url, { headers: { Accept: "text/html" }, credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("load failed");
                return response.text();
            })
            .then(function (html) {
                var doc = new DOMParser().parseFromString(html, "text/html");
                var form = doc.querySelector("form[data-customer-form]");
                if (!form) throw new Error("form missing");
                setModalBody("");
                var target = modalRoot().querySelector(".modal-body");
                target.appendChild(document.importNode(form, true));
                var firstField = target.querySelector("#first_name");
                if (firstField) firstField.focus();
            })
            .catch(function () {
                closeModal();
                window.location.href = url;
            });
    }

    /* ---------- Profile drawer ---------- */

    function drawerRoot() {
        return document.getElementById("drawer-root");
    }

    function closeDrawer() {
        var root = drawerRoot();
        if (root) root.innerHTML = "";
    }

    function avatarClassFromPage(trigger) {
        var row = trigger.closest("tr, .customer-card, .profile-card, .drawer");
        var avatar = row ? row.querySelector(".avatar") : null;
        if (avatar) {
            var match = /(avatar-\d)/.exec(avatar.className);
            if (match) return match[1];
        }
        return "avatar-0";
    }

    function openProfileDrawer(id, trigger) {
        closeDrawer();
        var root = drawerRoot();
        if (!root) {
            window.location.href = "/customers/" + id;
            return;
        }
        var overlay = document.createElement("div");
        overlay.className = "drawer-overlay";
        overlay.addEventListener("click", closeDrawer);
        var drawer = document.createElement("aside");
        drawer.className = "drawer";
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-modal", "true");
        drawer.setAttribute("aria-label", "Customer profile");
        drawer.innerHTML =
            '<div class="drawer-header"><div><h2 class="drawer-title">Customer Profile</h2>' +
            '<p class="drawer-subtitle">Customer #' + escapeHtml(id) + "</p></div>" +
            '<button type="button" class="modal-close" data-drawer-close aria-label="Close profile">×</button></div>' +
            '<div class="drawer-body"><p class="modal-loading">Loading profile…</p></div>';
        root.appendChild(overlay);
        root.appendChild(drawer);
        requestAnimationFrame(function () {
            overlay.classList.add("open");
            drawer.classList.add("open");
        });
        drawer.querySelector("[data-drawer-close]").addEventListener("click", closeDrawer);

        fetch("/customers/" + id, { headers: { Accept: "application/json" }, credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("not found");
                return response.json();
            })
            .then(function (payload) {
                renderDrawer(drawer, payload.customer, avatarClassFromPage(trigger));
            })
            .catch(function () {
                closeDrawer();
                showToast("Could not load that customer profile.", "error");
            });
    }

    function renderDrawer(drawer, customer, avatarClass) {
        var fullName = customer.first_name + " " + customer.last_name;
        function row(label, value, href) {
            var display = value ? escapeHtml(value) : "—";
            if (value && href) display = '<a href="' + href + escapeHtml(value) + '">' + display + "</a>";
            return '<div class="drawer-row"><dt>' + label + "</dt><dd>" + display + "</dd></div>";
        }
        var body = drawer.querySelector(".drawer-body");
        body.innerHTML =
            '<div class="drawer-profile"><span class="avatar avatar-lg ' + avatarClass + '" aria-hidden="true">' +
            escapeHtml(initials(customer.first_name, customer.last_name)) + "</span>" +
            '<p class="drawer-name">' + escapeHtml(fullName) + "</p>" +
            '<span class="badge">Customer #' + escapeHtml(customer.id) + "</span></div>" +
            '<dl class="drawer-list">' +
            row("Email", customer.email, "mailto:") +
            row("Phone", customer.phone, "tel:") +
            row("Address", customer.address) +
            row("City", customer.city) +
            row("Country", customer.country) +
            row("Registered", formatDate(customer.created_at)) +
            "</dl>" +
            '<div class="drawer-actions">' +
            '<a class="btn btn-secondary" href="/customers/' + customer.id + '/edit" data-action="edit" data-id="' + customer.id + '">Edit</a>' +
            '<a class="btn btn-outline-danger" href="/customers/' + customer.id + '/delete/confirm" data-action="delete" data-id="' + customer.id + '">Delete</a>' +
            "</div>";
    }

    /* ---------- Delete confirmation ---------- */

    function openDeleteDialog(id) {
        fetch("/customers/" + id, { headers: { Accept: "application/json" }, credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("missing");
                return response.json();
            })
            .then(function (payload) {
                var customer = payload.customer;
                var name = customer.first_name + " " + customer.last_name;
                var body =
                    '<div class="modal-danger-icon" aria-hidden="true">' +
                    '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg></div>' +
                    '<p class="modal-confirm-text">Are you sure you want to permanently delete <strong>' +
                    escapeHtml(name) + "</strong>? This action cannot be undone.</p>" +
                    '<form data-delete-form action="/customers/' + customer.id + '/delete" method="POST">' +
                    '<div class="form-actions"><button type="button" class="btn btn-secondary" data-modal-close>Cancel</button>' +
                    '<button type="submit" class="btn btn-danger" data-submit>Delete Customer</button></div></form>';
                openModal({ title: "Delete this customer?", size: "sm", body: body });
            })
            .catch(function () {
                showToast("That customer record no longer exists.", "error");
            });
    }

    /* ---------- Client-side validation (mirrors backend rules) ---------- */

    var EMAIL_PATTERN = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;
    var NAME_PATTERN = /^[\p{L} \-'\u2019]+$/u;

    function validateCustomerForm(form) {
        var errors = {};
        function value(name) {
            var field = form.elements[name];
            return field ? field.value.trim() : "";
        }
        function checkName(name, label) {
            var val = value(name);
            if (!val) { errors[name] = label + " is required."; return; }
            if (val.length < 2) { errors[name] = label + " must be at least 2 characters long."; return; }
            if (val.length > 50) { errors[name] = label + " must not exceed 50 characters."; return; }
            if (!NAME_PATTERN.test(val)) {
                errors[name] = label + " can only contain letters, spaces, hyphens, and apostrophes.";
            }
        }
        checkName("first_name", "First name");
        checkName("last_name", "Last name");

        var email = value("email");
        if (!email) {
            errors.email = "Email address is required.";
        } else if (email.length > 254) {
            errors.email = "Email address must not exceed 254 characters.";
        } else if (!EMAIL_PATTERN.test(email) || email.indexOf("..") !== -1) {
            errors.email = "Please enter a valid email address.";
        }

        var phoneRaw = value("phone");
        if (!phoneRaw) {
            errors.phone = "Phone number is required.";
        } else {
            var checkChars = phoneRaw.charAt(0) === "+" ? phoneRaw.slice(1) : phoneRaw;
            if (/[^0-9 \-().]/.test(checkChars)) {
                errors.phone = "Phone number contains invalid characters. Only digits, spaces, dashes, and parentheses are allowed.";
            } else {
                var digits = (phoneRaw.match(/\d/g) || []).length;
                if (digits < 7) errors.phone = "Phone number must have at least 7 digits.";
                else if (digits > 15) errors.phone = "Phone number must not exceed 15 digits.";
            }
        }

        [["address", "Address", 200], ["city", "City", 60], ["country", "Country", 60]].forEach(function (spec) {
            var val = value(spec[0]);
            if (val.length > spec[2]) errors[spec[0]] = spec[1] + " must not exceed " + spec[2] + " characters.";
        });
        return errors;
    }

    function clearClientErrors(form) {
        form.querySelectorAll(".invalid-feedback[data-client]").forEach(function (node) { node.remove(); });
        form.querySelectorAll(".form-control.is-invalid").forEach(function (input) { input.classList.remove("is-invalid"); });
        var summary = form.querySelector(".form-error-summary");
        if (summary) summary.remove();
    }

    function renderFormErrors(form, errors) {
        clearClientErrors(form);
        var names = Object.keys(errors);
        if (!names.length) return;
        var summary = document.createElement("div");
        summary.className = "form-error-summary";
        summary.setAttribute("role", "alert");
        summary.textContent = "Please correct the " + names.length + " highlighted field" + (names.length === 1 ? "." : "s.");
        form.insertBefore(summary, form.firstChild);
        names.forEach(function (name) {
            var input = form.elements[name];
            if (!input) return;
            input.classList.add("is-invalid");
            var group = input.closest(".form-group");
            var feedback = document.createElement("span");
            feedback.className = "invalid-feedback";
            feedback.setAttribute("data-client", "true");
            feedback.setAttribute("role", "alert");
            feedback.textContent = errors[name];
            if (group) group.appendChild(feedback);
        });
        var firstInvalid = form.querySelector(".form-control.is-invalid");
        if (firstInvalid) firstInvalid.focus();
    }

    /* ---------- Form submission over fetch ---------- */

    function setSubmitting(form, submitting) {
        var button = form.querySelector("[data-submit]");
        if (!button) return;
        if (submitting) {
            button.disabled = true;
            button.setAttribute("data-original-label", button.innerHTML);
            button.innerHTML = '<span class="btn-spinner" aria-hidden="true"></span> Saving…';
        } else {
            button.disabled = false;
            var original = button.getAttribute("data-original-label");
            if (original) button.innerHTML = original;
        }
    }

    function submitCustomerForm(form) {
        var errors = validateCustomerForm(form);
        if (Object.keys(errors).length) {
            renderFormErrors(form, errors);
            return;
        }
        setSubmitting(form, true);
        fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: { Accept: "application/json" },
            credentials: "same-origin"
        })
            .then(function (response) {
                var isJson = (response.headers.get("Content-Type") || "").indexOf("application/json") !== -1;
                if (!isJson) throw new Error("unexpected response");
                return response.json().then(function (payload) {
                    return { status: response.status, payload: payload };
                });
            })
            .then(function (result) {
                if (result.status === 200 || result.status === 201) {
                    queueToastAfterReload(result.payload.message || "Saved successfully.", "success");
                    window.location.reload();
                } else if (result.status === 422) {
                    setSubmitting(form, false);
                    renderFormErrors(form, result.payload.errors || {});
                } else {
                    throw new Error(result.payload.message || "request failed");
                }
            })
            .catch(function () {
                setSubmitting(form, false);
                showToast("Something went wrong while saving. Please try again.", "error");
            });
    }

    function submitDeleteForm(form) {
        setSubmitting(form, true);
        var data = new FormData();
        data.append("csrf_token", csrfToken());
        fetch(form.action, {
            method: "POST",
            body: data,
            headers: { Accept: "application/json" },
            credentials: "same-origin"
        })
            .then(function (response) {
                return response.json().catch(function () { return {}; }).then(function (payload) {
                    return { status: response.status, payload: payload };
                });
            })
            .then(function (result) {
                if (result.status === 200) {
                    queueToastAfterReload(result.payload.message || "Customer deleted.", "success");
                    window.location.reload();
                } else if (result.status === 404) {
                    closeModal();
                    showToast("That customer record no longer exists.", "error");
                } else {
                    throw new Error("delete failed");
                }
            })
            .catch(function () {
                setSubmitting(form, false);
                showToast("Something went wrong while deleting. Please try again.", "error");
            });
    }

    /* ---------- Live search ---------- */

    var searchTimer = null;
    var lastSearchValue = null;

    function initLiveSearch() {
        var form = document.getElementById("search-form");
        var input = document.getElementById("search-input");
        var results = document.getElementById("directory-results");
        if (!form || !input || !results) return;
        lastSearchValue = input.value;

        input.addEventListener("input", function () {
            if (input.value === lastSearchValue) return;
            window.clearTimeout(searchTimer);
            searchTimer = window.setTimeout(function () {
                runLiveSearch(form, input, results);
            }, 350);
        });
    }

    function runLiveSearch(form, input, results) {
        var query = input.value;
        lastSearchValue = query;
        var perPageSelect = document.getElementById("per_page");
        var params = new URLSearchParams({
            q: query,
            sort: form.getAttribute("data-sort") || "created_at",
            order: form.getAttribute("data-order") || "desc",
            per_page: perPageSelect ? perPageSelect.value : (form.getAttribute("data-per-page") || "10"),
            page: "1"
        });
        var url = form.action + "?" + params.toString();
        results.classList.add("is-loading");
        results.setAttribute("aria-busy", "true");
        fetch(url, { headers: { Accept: "text/html" }, credentials: "same-origin" })
            .then(function (response) {
                if (!response.ok) throw new Error("search failed");
                return response.text();
            })
            .then(function (html) {
                var doc = new DOMParser().parseFromString(html, "text/html");
                var fresh = doc.getElementById("directory-results");
                if (fresh) {
                    results.innerHTML = fresh.innerHTML;
                    window.history.replaceState(null, "", url);
                }
            })
            .catch(function () { /* keep current results; Search button still works */ })
            .finally(function () {
                results.classList.remove("is-loading");
                results.removeAttribute("aria-busy");
            });
    }

    /* ---------- Global event wiring ---------- */

    function initActions() {
        document.addEventListener("click", function (event) {
            var modalClose = event.target.closest("[data-modal-close]");
            if (modalClose && modalClose.closest("#modal-root")) {
                event.preventDefault();
                closeModal();
                return;
            }

            var createTrigger = event.target.closest('[data-modal="create"]');
            if (createTrigger) {
                event.preventDefault();
                closeAllMenus(null);
                openFormModal(createTrigger.getAttribute("href"), "Register New Customer", "Enter details to create a new customer record.");
                return;
            }

            var actionTrigger = event.target.closest("[data-action]");
            if (!actionTrigger) return;
            var action = actionTrigger.getAttribute("data-action");
            var id = actionTrigger.getAttribute("data-id");
            if (!id) return;
            if (action === "view") {
                event.preventDefault();
                closeAllMenus(null);
                openProfileDrawer(id, actionTrigger);
            } else if (action === "edit") {
                event.preventDefault();
                closeAllMenus(null);
                closeDrawer();
                openFormModal("/customers/" + id + "/edit", "Edit Customer", "Update the customer record below.");
            } else if (action === "delete") {
                event.preventDefault();
                closeAllMenus(null);
                closeDrawer();
                openDeleteDialog(id);
            }
        });

        document.addEventListener("submit", function (event) {
            var form = event.target;
            if (form.matches("form[data-customer-form]")) {
                event.preventDefault();
                submitCustomerForm(form);
            } else if (form.matches("form[data-delete-form]")) {
                event.preventDefault();
                submitDeleteForm(form);
            }
        });

        document.addEventListener("input", function (event) {
            var input = event.target;
            if (input.classList && input.classList.contains("is-invalid") && input.form) {
                input.classList.remove("is-invalid");
                var group = input.closest(".form-group");
                var clientError = group ? group.querySelector(".invalid-feedback[data-client]") : null;
                if (clientError) clientError.remove();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key !== "Escape") return;
            if (modalRoot() && modalRoot().firstChild) closeModal();
            else if (drawerRoot() && drawerRoot().firstChild) closeDrawer();
            else if (document.body.classList.contains("sidebar-open")) {
                document.body.classList.remove("sidebar-open");
                var menu = document.getElementById("topbar-menu");
                if (menu) menu.setAttribute("aria-expanded", "false");
            }
        });

        var perPage = document.getElementById("per_page");
        if (perPage && perPage.hasAttribute("data-autosubmit")) {
            perPage.addEventListener("change", function () {
                if (perPage.form) perPage.form.submit();
            });
        }
    }

    /* ---------- Boot ---------- */

    document.addEventListener("DOMContentLoaded", function () {
        initSidebar();
        initMenus();
        initActions();
        initLiveSearch();
        enhanceServerToasts();
        showPendingToast();
    });
})();
