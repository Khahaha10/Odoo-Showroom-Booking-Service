import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CarVisitWizard = publicWidget.Widget.extend({
  selector: "#carVisitForm",
  events: {
    "click .visit-next-step": "_onNextStep",
    "click .visit-prev-step": "_onPrevStep",
  },

  start: function () {
    this.currentStep = 1;
    this.totalSteps = 3;
    this.progressBar = document.getElementById("visitProgressBar");
    return this._super.apply(this, arguments);
  },

  _updateStep: function (step) {
    this.el
      .querySelectorAll(".visit-step-content")
      .forEach((el) => el.classList.add("d-none"));
    const targetStep = this.el.querySelector("#v-step" + step);
    if (targetStep) targetStep.classList.remove("d-none");

    const progressWidth = ((step - 1) / (this.totalSteps - 1)) * 100;
    if (this.progressBar) this.progressBar.style.width = progressWidth + "%";

    const wrapper = this.el.closest(".oe_structure");
    for (let i = 1; i <= this.totalSteps; i++) {
      const ind = wrapper.querySelector("#v-ind_" + i);
      const lbl = wrapper.querySelector("#v-label_" + i);
      if (i <= step) {
        if (ind) ind.classList.add("active");
        if (lbl) lbl.classList.add("active");
      } else {
        if (ind) ind.classList.remove("active");
        if (lbl) lbl.classList.remove("active");
      }
    }

    const card = this.el.closest(".card");
    if (card) card.scrollIntoView({ behavior: "smooth", block: "center" });
  },

  _onNextStep: function (ev) {
    ev.preventDefault();
    const currentStepDiv = this.el.querySelector("#v-step" + this.currentStep);
    const inputs = currentStepDiv.querySelectorAll(
      "input[required], select[required], textarea[required]"
    );
    let isValid = true;

    inputs.forEach((input) => {
      if (!input.value) {
        isValid = false;
        input.classList.add("is-invalid");
        input.addEventListener(
          "input",
          () => input.classList.remove("is-invalid"),
          { once: true }
        );
      } else {
        input.classList.remove("is-invalid");
      }
    });

    if (isValid) {
      this.currentStep++;
      this._updateStep(this.currentStep);
    }
  },

  _onPrevStep: function (ev) {
    ev.preventDefault();
    if (this.currentStep > 1) {
      this.currentStep--;
      this._updateStep(this.currentStep);
    }
  },
});
