google.load('visualization', '1', {packages: ['corechart']});
google.setOnLoadCallback(drawChart);


$(document).ready(function(){ initialize() });

function initialize() {
	if($("body").hasClass("map")){
		var latlng = new google.maps.LatLng(15.824283,120.478516);
		var myOptions = {
			zoom: 4,
			center: latlng,
			disableDefaultUI: true,
			mapTypeId: google.maps.MapTypeId.SATELLITE,
			draggable: false,
			scrollwheel: false
		};
		var map = new google.maps.Map(document.getElementById("content"), myOptions);
		$.ajax({ url: "/aqi/cities/list", context: document.body, dataType: 'json', success: function(data){
			for(var i = 0; i < data.length; i++){
				var city = data[i];
				var p = new ACACityOverlay(
					city.key,
					new google.maps.LatLng(city.location.lat, city.location.lon),
					city.name, city.current_aqi, 1001 + i, map
				);
			}
		}});
	}
	else if($("body").hasClass("cty")){
		var k = cityKey();
		$.ajax({ url: "/aqi/cities/show?k=" + k, context: document.body, dataType: 'json', success: function(data){
			var latlng = new google.maps.LatLng(data.location.lat, data.location.lon);
			var myOptions = {
				zoom: 12,
				center: latlng,
				disableDefaultUI: true,
				mapTypeId: google.maps.MapTypeId.SATELLITE,
				draggable: false,
				scrollwheel: false
			};
			var map = new google.maps.Map(document.getElementById("map"), myOptions);
		}})
		$(".aqi").each(function(i, element){
			$(element).addClass(airQuality($(element).html()))
		})
	}
	
	var now = new Date();
	$(".cityDropdown").bind({
		change: function(){
			document.location.href = "/city?k=" + this.value;
		}
	});
}

function cityKey(){
	var maps = $(".citymap");
	if(maps && maps.length > 0){
		return maps[0].className.split(" ")[1].split("_")[1];	
	}
}

function drawChart(){
	var k = cityKey();
	var container = document.getElementById('aqiChart');
	if(k && container){
		$.ajax({ url: "/aqi/data?k=" + k, context: document.body, dataType: 'json', success: function(records){
			var data = new google.visualization.DataTable();
			data.addColumn('date', 'Date');
			data.addColumn('number', 'AQI');
			data.addRows(records.length);
			var last_r = 0;
			for(var r = 0; r < records.length; r++){
				var record = records[r];
				data.setValue(r, 0, new Date(record.timestamp));
				data.setValue(r, 1, record.aqi);
				last_r = record.aqi;
			}

			var chart = new google.visualization.LineChart(container);
			chart.draw(data, {
				width: 600, height: 200,
				legend: 'none',
				vAxis: {maxValue: 500, minValue: 0, baseline: last_r}}
			);
		}});
	}

}

function ACACityOverlay(k, l, n, v, z, map) {
	this.latlng = l;
	this.key = k;
	this.cityName = n;
	this.aqiValue = v;
	this.z = z;

	this.div = null;

	this.setMap(map);
}

ACACityOverlay.prototype = new google.maps.OverlayView();

ACACityOverlay.prototype.onAdd = function() {
	var containerDiv = document.createElement('div');
	containerDiv.className = "city";
	containerDiv.style.border = "none";
	containerDiv.style.borderWidth = "0px";
	containerDiv.style.position = "absolute";

	var cityText = document.createElement("div");
	cityText.className = "name";
	cityText.innerHTML = "<a href=\"/city?k=" + this.key + "\">" + this.cityName + "</a>";
	containerDiv.appendChild(cityText);

	var aqiText = document.createElement("div");
	aqiText.className = "aqi " + airQuality(this.aqiValue);
	if(this.aqiValue){
		aqiText.innerHTML = "<div class=\"label\">AQI</div><div class=\"value\">" + (this.aqiValue) + "</div>";
	}
	else{
		aqiText.innerHTML = "<div class=\"label\">No Data</div>";
	}
	containerDiv.appendChild(aqiText);

	this.div = containerDiv;

	var ref = this;
	this.getPanes().floatPane.appendChild(containerDiv);
	$(containerDiv).bind({
		click: function(){
			document.location.href = "/city?k=" + ref.key;
		},
		mouseenter: function(){
			containerDiv.style.zIndex = 2001;
		},
		mouseleave: function(){
			containerDiv.style.zIndex = ref.z;
		}
	})
}

ACACityOverlay.prototype.draw = function(){
	var overlayProjection = this.getProjection();
	var pt = overlayProjection.fromLatLngToDivPixel(this.latlng);
	var d = this.div;

	d.style.left = (pt.x - 50) + 'px';
	d.style.top = (pt.y - 10) + 'px';
}

function airQuality(aqi){
	if(!aqi) return "nodata";
	if(aqi <= 25) return "low";
	if(aqi <= 50) return "moderate";
	if(aqi <= 100) return "elevated";
	if(aqi <= 200) return "unhealthy";
	return "dangerous";
}