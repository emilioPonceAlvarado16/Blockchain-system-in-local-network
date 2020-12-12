$(document).ready(function() {
	$(chart_id).highcharts({
		chart: chart,
		title: title,
		mapNavigation:mapNavigation,
		tooltip:tooltip,
		series: series,
		credits:credits,
	});
});