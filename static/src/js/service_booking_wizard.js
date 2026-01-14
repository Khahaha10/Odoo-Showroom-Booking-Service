/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ServiceBookingWizard = publicWidget.Widget.extend({
  selector: "#bookingForm",
  events: {
    "click .next-step": "_onNextStep",
    "click .prev-step": "_onPrevStep",
    "change #customer_vehicle_select": "_onVehicleChange",
  },

  start: function () {
    this.currentStep = 1;
    this.totalSteps = 3;
    this.progressBar = document.getElementById("progressBar");
    this.progressBar = this.el
      .closest(".oe_structure")
      .querySelector("#progressBar");

    return this._super.apply(this, arguments);
  },

  _updateStep: function (step) {
    this.el
      .querySelectorAll(".step-content")
      .forEach((el) => el.classList.add("d-none"));
    const targetStep = this.el.querySelector("#step" + step);
    if (targetStep) {
      targetStep.classList.remove("d-none");
    }

    const progressWidth = ((step - 1) / (this.totalSteps - 1)) * 100;
    if (this.progressBar) {
      this.progressBar.style.width = progressWidth + "%";
    }
    const wrapper = this.el.closest(".oe_structure");

    for (let i = 1; i <= this.totalSteps; i++) {
      const indicator = wrapper.querySelector("#ind_" + i);
      const label = wrapper.querySelector("#label_" + i);

      if (i <= step) {
        if (indicator) indicator.classList.add("active");
        if (label) label.classList.add("active");
      } else {
        if (indicator) indicator.classList.remove("active");
        if (label) label.classList.remove("active");
      }
    }

    const card = this.el.closest(".card");
    if (card) {
      card.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  },

  _onNextStep: function (ev) {
    ev.preventDefault();

    const currentStepDiv = this.el.querySelector("#step" + this.currentStep);
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

  _onVehicleChange: function (ev) {
    const select = ev.currentTarget;
    const selectedOption = select.options[select.selectedIndex];

    if (selectedOption.value) {
      try {
        let dataStr = selectedOption
          .getAttribute("data-vehicle")
          .replace(/'/g, '"');
        const vehicleData = JSON.parse(dataStr);

        this.el.querySelector("#plat_number").value = vehicleData.plate || "";
        this.el.querySelector("#vehicle_brand").value =
          vehicleData.brand_id || "";
        this.el.querySelector("#vehicle_model").value =
          vehicleData.model_id || "";
        this.el.querySelector("#vehicle_year_manufacture").value =
          vehicleData.year || "";
      } catch (e) {
        console.error("Error parsing vehicle data", e);
      }
    } else {
      this.el.querySelector("#plat_number").value = "";
      this.el.querySelector("#vehicle_brand").value = "";
      this.el.querySelector("#vehicle_model").value = "";
      this.el.querySelector("#vehicle_year_manufacture").value = "";
    }
  },
});
