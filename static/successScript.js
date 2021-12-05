window.onload = function () {
  let hidden = document.getElementById("hidden");
  let refButtonDiv = document.getElementById("genreButtons");

  selectedGenres = hidden.value;

  for (var i = 0; i < refButtonDiv.children.length; i++) {
    let button = refButtonDiv.children[i].children[0];
    if (selectedGenres.includes(button.name)) {
      button.classList.add("is-focused");
    }
  }
};
