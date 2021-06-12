function playerShares() {
	var x = document.getElementsByClassName("owned");
	var y = document.getElementsByClassName("available");
	var z = document.getElementsByClassName("not-available");
	if (y[0].parentElement.style.display != "none") {
		for (i = 0; i < y.length; i++) {
			y[i].parentElement.style.display = "none";
		}
		for (i = 0; i < z.length; i++) {
			z[i].parentElement.style.display = "none";
		}
	}else {
		for (i = 0; i < y.length; i++) {
			y[i].parentElement.style.display = "table-row";
		}
		for (i = 0; i < z.length; i++) {
			z[i].parentElement.style.display = "table-row";
		}
	}	
}