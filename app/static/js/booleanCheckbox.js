/* https://www.binwang.me/2024-06-08-Create-a-Checkbox-That-Returns-Boolean-Value-for-htmx.html */
(function(){
  class BooleanCheckbox extends HTMLInputElement {
      constructor() {
          super();
      }

      get checked() {
          return true;
      }

      get value() {
          if (super.checked) {
              return true;
          } else {
              return false;
          }
      }
  }
  customElements.define("boolean-checkbox", BooleanCheckbox, { extends: "input" });
})();
