function favoriteTeam() {
	var x = document.getElementById("team");
	var y = document.getElementById("teamcss");
	var z = document.getElementById("fave-team");
	y.href = "/static/css/" + x.value + ".css";

}