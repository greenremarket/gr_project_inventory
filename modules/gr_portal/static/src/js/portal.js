/** @odoo-module **/

/**
 * Green Remarket — Portal Widget (Odoo 17)
 *
 * Adds staggered fade-in animation to portal tile cards on the
 * /my home page (grm_website.portal_my_home_custom with gr_portal banner).
 *
 * The animate-fade-in CSS class and @keyframes portalFadeIn are
 * defined in portal.css.
 */

import publicWidget from "@web/legacy/js/public/public_widget";

const GreenRemarketPortal = publicWidget.Widget.extend({
    selector: ".o_portal_wrap",

    start() {
        const result = this._super(...arguments);
        this._initCardAnimations();
        return result;
    },

    _initCardAnimations() {
        // Staggered fade-in for portal tiles
        this.$(".o_portal_tile").each(function (index) {
            $(this)
                .css("animation-delay", (index * 0.05) + "s")
                .addClass("animate-fade-in");
        });
    },
});

publicWidget.registry.GreenRemarketPortal = GreenRemarketPortal;
export default GreenRemarketPortal;
