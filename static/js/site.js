document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");

  menuButton?.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    menu?.classList.toggle("is-open", !expanded);
  });

  document.querySelectorAll("[data-dismiss]").forEach((button) => {
    button.addEventListener("click", () => button.closest(".notice")?.remove());
  });

  document.querySelectorAll("[data-confirm]").forEach((button) => {
    button.closest("form")?.addEventListener("submit", (event) => {
      if (!window.confirm(button.dataset.confirm)) event.preventDefault();
    });
  });

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type='submit']");
      if (button && !button.disabled) {
        button.classList.add("is-loading");
        button.setAttribute("aria-busy", "true");
      }
    });
  });

  document.querySelectorAll(".product-image, .detail-image img, .cart-thumb img").forEach((image) => {
    image.addEventListener("error", () => {
      image.closest(".product-image-wrap, .detail-image, .cart-thumb")?.classList.add("image-failed");
      image.remove();
    }, { once: true });
  });
});