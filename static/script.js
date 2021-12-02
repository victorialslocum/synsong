window.onload = function () {
  let refButtonDiv = document.getElementById("genreButtons");
  let inputForm = document.getElementById("inputForm");
  let hiddenElement = document.getElementById("hidden");
  let submitButton = document.getElementById("submitButton");
  let genreList = [];
  console.log(inputForm);
  console.log(refButtonDiv);
  for (var i = 0; i < refButtonDiv.children.length; i++) {
    let button = refButtonDiv.children[i];

    button.onclick = function () {
      if (this.classList.contains("is-focused")) {
        this.classList.remove("is-focused");
      } else {
        this.classList.add("is-focused");
      }
    };
  }

  submitButton.onclick = function () {
    console.log("success");
    for (var i = 0; i < refButtonDiv.children.length; i++) {
      let button = refButtonDiv.children[i];
      if (button.classList.contains("is-focused")) {
        console.log(button.value);
        genreList.push(button.value);
      }
    }
    console.log(genreList);
    hiddenElement.setAttribute("value", genreList);
    console.log(hiddenElement);
    inputForm.submit();
  };
};
