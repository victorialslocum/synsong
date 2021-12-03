window.onload = function () {
  let refButtonDiv = document.getElementById("genreButtons");
  let publicButton = document.getElementById("publicButton");
  let visDiv = document.getElementById("visibility");
  let privateButton = document.getElementById("privateButton");
  let inputForm = document.getElementById("inputForm");
  let hiddenElement = document.getElementById("hidden");
  let submitButton = document.getElementById("submitButton");
  let genreList = [];
  console.log(inputForm);
  console.log(refButtonDiv);
  for (var i = 0; i < refButtonDiv.children.length; i++) {
    let button = refButtonDiv.children[i].children[0];
    console.log(button);

    button.onclick = function () {
      if (this.classList.contains("is-focused")) {
        this.classList.remove("is-focused");
      } else {
        this.classList.add("is-focused");
      }
    };
  }

  publicButton.onclick = function () {
    if (publicButton.classList.contains("is-focused")) {
      privateButton.classList.add("is-focused");
      publicButton.classList.remove("is-focused");
    } else {
      publicButton.classList.add("is-focused");
      privateButton.classList.remove("is-focused");
    }
  };

  privateButton.onclick = function () {
    if (privateButton.classList.contains("is-focused")) {
      publicButton.classList.add("is-focused");
      privateButton.classList.remove("is-focused");
    } else {
      privateButton.classList.add("is-focused");
      publicButton.classList.remove("is-focused");
    }
  };

  submitButton.onclick = function () {
    console.log("success");
    for (var i = 0; i < refButtonDiv.children.length; i++) {
      let button = refButtonDiv.children[i].children[0];
      if (button.classList.contains("is-focused")) {
        console.log(button.name);
        genreList.push(button.name);
      }
    }
    console.log(genreList);
    hiddenElement.setAttribute("value", genreList);
    console.log(hiddenElement);
    inputForm.submit();
  };
};
