/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

/**
 * GR Login Widget
 *
 * Handles three behaviours on the video-background login page:
 *  1. Page loader: hides once the background video fires `canplaythrough`
 *     (4-second fallback in case the video never loads).
 *  2. "Commencer maintenant" CTA: hides the hero, shows the login form.
 *  3. "Retour" back link: hides the form, restores the hero.
 */
publicWidget.registry.GRLogin = publicWidget.Widget.extend({
    selector: '.o_login_page',

    events: {
        'click [data-action="show-login"]': '_onShowLogin',
        'click [data-action="show-hero"]':  '_onShowHero',
    },

    start() {
        const result = this._super(...arguments);
        this._initLoader();
        return result;
    },

    // ─── Loader ───────────────────────────────────────────────────────────────

    _initLoader() {
        const loader = document.getElementById('gr_login_loader');
        if (!loader) return;

        const hide = () => {
            loader.classList.add('o_login_loader_hidden');
            setTimeout(() => loader.remove(), 600);
        };

        // Auto-hide after 4 s as a safety fallback
        const timer = setTimeout(hide, 4000);

        const video = document.getElementById('gr_login_video');
        if (video) {
            video.addEventListener('canplaythrough', () => {
                clearTimeout(timer);
                hide();
            }, { once: true });
        } else {
            // No video element on this page — hide immediately
            clearTimeout(timer);
            hide();
        }
    },

    // ─── Hero ↔ Form toggle ──────────────────────────────────────────────────

    _onShowLogin(ev) {
        ev.preventDefault();
        const hero      = this.el.querySelector('#gr_login_hero');
        const container = this.el.querySelector('.oe_website_login_container');
        const back      = this.el.querySelector('.o_login_back');

        if (hero)      hero.style.display = 'none';
        if (container) container.style.display = '';
        if (back)      back.style.display = '';

        // Focus the first input in the form
        if (container) {
            const first = container.querySelector('input[autofocus], input[type="email"], input[name="login"]');
            if (first) first.focus();
        }
    },

    _onShowHero(ev) {
        ev.preventDefault();
        const hero      = this.el.querySelector('#gr_login_hero');
        const container = this.el.querySelector('.oe_website_login_container');
        const back      = this.el.querySelector('.o_login_back');

        if (hero)      hero.style.display = '';
        if (container) container.style.display = 'none';
        if (back)      back.style.display = 'none';
    },
});

export default publicWidget.registry.GRLogin;
