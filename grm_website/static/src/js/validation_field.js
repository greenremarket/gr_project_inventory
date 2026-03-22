/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.ContactFormValidation = publicWidget.Widget.extend({
    selector: 'form',

    start() {
        this.$submitBtn = this.$el.find(".s_website_form_send");

        this.$submitBtn.prop("disabled", true).addClass("disabled");

        this.$el.find("input[type='email'], input[type='tel'], input[name='zip']")
            .on("input change", (ev) => {
                this._validateField(ev.target);
                this._updateSubmitButton();
            });

        this.$el.find("input[name='name'], textarea[name='description'], input[name='subject']")
            .on("blur", (ev) => {
                this._validateField(ev.target);
                this._updateSubmitButton();
            });

        this.$el.on("submit", (ev) => this._validateFormFull(ev));

        return this._super(...arguments);
    },

    _validateField(input) {
        this._clearErrors(input);
        const value = input.value.trim();

        if (input.name === "name") {
            const nameRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$/;
            if (!value) this._showError(input, "Le nom complet est requis.");
            else if (!nameRegex.test(value)) this._showError(input, "Le nom ne doit contenir que des lettres, espaces, tirets ou apostrophes.");
        }
        else if (input.type === "email") {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) this._showError(input, "Adresse e-mail invalide.");
        }
        else if (input.type === "tel") {
            const internationalRegex = /^\+[0-9\s\-]{7,15}$/;
            const frenchRegex = /^0[0-9\s\-]{8,14}$/;
            if (value && !(internationalRegex.test(value) || frenchRegex.test(value))) {
                this._showError(input, "Numéro de téléphone invalide (doit commencer par + ou 0).");
            }
        }
        else if (input.name === "description" || input.name === "subject") {
            const words = value.split(/\s+/).filter(Boolean);
            if (words.length < 2) this._showError(input, "Doit contenir au moins une phrase.");
        }
        else if (input.name === "zip") {
            const zipRegex = /^[0-9]{5}$/;
            if (!zipRegex.test(value)) this._showError(input, "Code postal invalide.");
        }
    },

    _validateFormFull(ev) {
        ev.preventDefault();
        let valid = true;
        this.$el.find("textarea[name='description'], input[name='subject'], input[name='name'], input[type='email'], input[type='tel'], input[name='zip']").each((i, input) => {
            this._validateField(input);
            if ($(input).hasClass("is-invalid")) valid = false;
        });
        if (valid) this.$el[0].submit();
    },

    _updateSubmitButton() {
        let valid = true;
        this.$el.find("textarea[name='description'], input[name='subject'], input[name='name'], input[type='email'], input[type='tel'], input[name='zip']").each((i, input) => {
            if ($(input).hasClass("is-invalid") || !input.value.trim()) valid = false;
        });
        if (valid) this.$submitBtn.prop("disabled", false).removeClass("disabled");
        else this.$submitBtn.prop("disabled", true).addClass("disabled");
    },

    _showError(input, message) {
        input.classList.add("is-invalid");
        const error = document.createElement("div");
        error.className = "text-danger small mt-1 input-error";
        error.textContent = message;
        input.parentElement.appendChild(error);
    },

    _clearErrors(input) {
        const $input = $(input);
        $input.next(".input-error").remove();
        $input.removeClass("is-invalid");
    }
});
