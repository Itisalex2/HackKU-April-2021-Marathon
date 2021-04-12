function speed() {
	if (document.getElementById("speed").value == "") {
		document.getElementById("cube").style.animationDuration = "8s";
	}
	else {
		document.getElementById("cube").style.animationDuration = `${Number(document.getElementById("speed").value)}s`;
	}
}

setInterval(speed, 100);
