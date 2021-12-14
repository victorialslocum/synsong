document.onreadystatechange = function () {
  const loader = document.getElementById("loader");
  if (document.readyState !== "complete") {
    document.querySelector("body").style.visibility = "hidden";
    loader.style.visibility = "visible";
  } else {
    loader.style.visibility = "hidden";
    document.querySelector("body").style.visibility = "visible";
  }
};

window.onload = function () {
  if (window.matchMedia("(max-width: 767px)").matches) {
    const dropdownitem = document.getElementById("dropdownitem");
    const dropdown = document.getElementById("dropdown");

    dropdown.style.display = "none";

    //Register the click event on the dropdown list
    dropdownitem.addEventListener("click", () => {
      if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
      } else {
        dropdown.style.display = "block";
      }
    });
  }

  const navbarBurger = document.getElementById("navburger");
  console.log(navbarBurger);

  navbarBurger.addEventListener("click", () => {
    const target = navbarBurger.dataset.target;
    const $target = document.getElementById(target);

    // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
    navbarBurger.classList.toggle("is-active");
    $target.classList.toggle("is-active");
  });
};
