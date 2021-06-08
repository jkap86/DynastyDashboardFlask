function playerShares() {
	var x = document.getElementsByClassName("owned");
	var y = document.getElementsByClassName("available");
	var z = document.getElementsByClassName("not-available");
	if (y[0].style.display != "none") {
		for (i = 0; i < y.length; i++) {
			y[i].style.display = "none";
		}
		for (i = 0; i < z.length; i++) {
			z[i].style.display = "none";
		}
	}else {
		for (i = 0; i < y.length; i++) {
			y[i].style.display = "table-cell";
		}
		for (i = 0; i < z.length; i++) {
			z[i].style.display = "table-cell";
		}
	}	
}