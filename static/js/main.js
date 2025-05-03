function initMap() {
    const center = { lat: 40.7128, lng: -74.0060 }; // Default center (New York City)
    
    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 14,
      center: center,
    });
  
    if (Array.isArray(foodEvents)) {
      foodEvents.forEach(event => {
        const marker = new google.maps.Marker({
          position: { lat: event.lat, lng: event.lng },
          map: map,
          title: event.title,
        });
  
        const infoWindow = new google.maps.InfoWindow({
          content: `<strong>${event.title}</strong><br>${event.description}<br><em>${event.location}</em>`,
        });
  
        marker.addListener("click", () => {
          infoWindow.open(map, marker);
        });
      });
    } else {
      console.warn("foodEvents is not an array");
    }
  }
  