function favoriteTeam() {
	var x = document.getElementById("team");
	var y = document.getElementById("teamcss");
	y.href = "/static/css/" + x.value + ".css";


}