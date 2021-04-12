function change() {
	var y = Math.random();
	if (y < 0.5) {
		document.getElementById("image").src = "image.png";
	}
	else {
		document.getElementById("image").src = "image.jpg";
	}
	setTimeout(change, 2000);
}
