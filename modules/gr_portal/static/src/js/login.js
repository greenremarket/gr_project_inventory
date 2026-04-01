/** @odoo-module **/

/**
 * Green Remarket — Login Page Widget (Odoo 17)
 *
 * Works WITH grm_website’s existing login template.
 * grm_website already provides:
 *   - Password eye toggle (#showPass in .custom-passoword)
 *   - Pill-shaped inputs ($input-border-radius: 120px)
 *   - Rounded buttons ($btn-border-radius: 80px)
 *   - Poppins font
 *
 * This widget adds:
 *   1. Page loader: hides when video is ready (or after 4s fallback)
 *   2. Hero ↔ Login form toggle with smooth jQuery fade transitions
 *
 * Updated 2026-04-01 (Lovable refresh):
 *   - Loader uses readyState >= 4 check instead of CSS class
 *   - Transitions use jQuery fadeIn/fadeOut for smooth animation
 *   - Event selectors changed from data-action to class-based
 */

import publicWidget from "@web/legacy/js/public/public_widget";

const GRLoginPage = publicWidget.Widget.extend({
    selector: ".o_login_page",

    events: {
        "click .o_login_cta":  "_onShowLogin",
        "click .o_login_back": "_onShowHero",
    },

    start() {
        const result = this._super(...arguments);
        // Hero, form, and back link are INSIDE .o_login_page — use this.$()
        this.$hero          = this.$(".o_login_hero");
        this.$formContainer = this.$(".oe_website_login_container");
        this.$back          = this.$(".o_login_back");
        // Loader and video are SIBLINGS of .o_login_page (outside the section).
        // this.$() only searches within the widget root, so use document-level $().
        this.$loader = $("#gr_login_loader");
        this._initVideoLoader();
        return result;
    },

    // ─── Page Loader ───

    _initVideoLoader() {
        // video is also outside .o_login_page — use document-level $()
        const $video = $("video.o_login_video_bg");
        if (!this.$loader.length) {
            return; // no loader in DOM, nothing to hide
        }
        if (!$video.length) {
            // No video element — hide loader immediately
            this._hideLoader();
            return;
        }
        const video = $video[0];
        // Video already buffered enough
        if (video.readyState >= 4) {
            this._hideLoader();
        } else {
            $video.one("canplaythrough", () => this._hideLoader());
        }
        // Safety fallback: hide after 4 s regardless
        this._loaderTimeout = setTimeout(() => this._hideLoader(), 4000);
    },

    _hideLoader() {
        if (this._loaderTimeout) {
            clearTimeout(this._loaderTimeout);
            this._loaderTimeout = null;
        }
        if (this.$loader && this.$loader.length) {
            this.$loader.fadeOut(500, () => this.$loader.remove());
        }
    },

    // ─── Hero → Login ───

    _onShowLogin(ev) {
        ev.preventDefault();
        this.$hero.fadeOut(200, () => {
            this.$formContainer.fadeIn(200);
            this.$back.fadeIn(200);
            this.$("input[name='login']").trigger("focus");
        });
    },

    // ─── Login → Hero ───

    _onShowHero(ev) {
        ev.preventDefault();
        this.$formContainer.fadeOut(200, () => {
            this.$back.fadeOut(200);
            this.$hero.fadeIn(200);
        });
    },

    destroy() {
        if (this._loaderTimeout) {
            clearTimeout(this._loaderTimeout);
        }
        this._super(...arguments);
    },
});

publicWidget.registry.GRLoginPage = GRLoginPage;
export default GRLoginPage;
