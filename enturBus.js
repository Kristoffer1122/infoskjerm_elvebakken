async function fetchDepartures() {
  const url = "https://api.entur.io/journey-planner/v3/graphql";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "ET-Client-Name": "Infoboard-app",
      },
      body: JSON.stringify({
        query: `
          {
            stopPlace(id: "NSR:StopPlace:6435") {
              id
              name
              estimatedCalls(timeRange: 72100, numberOfDepartures: 10) {
                realtime
                aimedArrivalTime
                expectedArrivalTime
                destinationDisplay {
                  frontText
                }
                serviceJourney {
                  journeyPattern {
                    line {
                      id
                      transportMode
                    }
                  }
                }
              }
            }
          }
        `,
      }),
    });

    if (!response.ok) {
      throw new Error(`Response ${response.status}`);
    }

    departuresData = await response.json();
    showDepartures()
    // console.dir(departuresData.data.stopPlace, { depth: null });
  } catch (error) {
    console.error("Fetch error:", error.message);
  }
}



setInterval(fetchDepartures, 30000);
fetchDepartures()


function showDepartures() {
  //document.getElementById("showText").innerHTML = "aimed arrival: " + departuresData.data.stopPlace.estimatedCalls[0].aimedArrivalTime;
  //document.getElementById("showText2").innerHTML = "expected arrival: " + departuresData.data.stopPlace.estimatedCalls[0].expectedArrivalTime;

  for (let call of departuresData.data.stopPlace.estimatedCalls) {
  let aimedArrival = call.aimedArrivalTime;

  let expectedArrival = new Date(call.expectedArrivalTime);
  let now = new Date()
  let timeDiff = Math.floor((expectedArrival - now) / 1000 / 60)

  if (timeDiff <= 0) {
    timeDiff = "nå"
  }

  let frontText = call.destinationDisplay.frontText;
  let lineId = call.serviceJourney.journeyPattern.line.id.split(":").pop()
  
  
  console.log(`${lineId} ${frontText}: ${timeDiff}`)
  }
    console.log("-------------------------")
}


setInterval(showDepartures, 9000);



