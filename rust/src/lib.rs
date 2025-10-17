use wasm_bindgen::prelude::*;
use gloo_net::http::Request;
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc, TimeZone, Datelike, Duration};
use gloo_utils::format::JsValueSerdeExt;
use urlencoding::encode;

#[derive(Serialize, Deserialize, Clone)]
pub struct BusAssignment {
    pub name: String,
    pub origin: String,
    pub destination: String,
    pub dep: String,
    pub arr: String,
    pub first_possible: bool, // true if this ferry is the earliest for this bus
}

#[derive(Serialize, Deserialize)]
pub struct Ferry {
    pub ferry_dep: String,
    pub buses: Vec<BusAssignment>,
}

async fn get_stop_id(name: &str) -> Result<String, JsValue> {
    let url = format!("https://v6.db.transport.rest/locations?query={}&results=1", encode(name));
    let resp = Request::get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    let data: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    let id = data
        .as_array()
        .and_then(|arr| arr.get(0))
        .and_then(|obj| obj.get("id"))
        .and_then(|v| v.as_str())
        .ok_or("Stop ID not found")?;
    Ok(id.to_string())
}

#[wasm_bindgen]
pub async fn fetch_ferries(from: &str, to: &str) -> Result<JsValue, JsValue> {
    let from_id = get_stop_id(from).await?;
    let to_id = get_stop_id(to).await?;

    let url = format!(
        "https://v6.db.transport.rest/journeys?from={}&to={}&results=50&products[bus]=true",
        encode(&from_id),
        encode(&to_id)
    );

    let resp = Request::get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    let data: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
    let journeys = data["journeys"].as_array().ok_or("No journeys")?;

    // Hardcoded ferry schedule: every hour :05, :20, :35, :50
    let ferry_minutes = [5, 20, 35, 50];
    let mut ferry_map: Vec<Ferry> = Vec::new();
    for hour in 0..24 {
        for &min in &ferry_minutes {
            ferry_map.push(Ferry {
                ferry_dep: format!("{:02}:{:02}", hour, min),
                buses: Vec::new(),
            });
        }
    }

    // Minimum travel time before arrival
    let min_travel = Duration::minutes(10);

    // Assign ferries to buses
    for j in journeys {
        let legs = j["legs"].as_array().unwrap();
        let first_leg = &legs[0];
        let last_leg = &legs[legs.len() - 1];

        let bus_name = first_leg["line"]["name"]
            .as_str()
            .unwrap_or(first_leg["mode"].as_str().unwrap_or("Bus"))
            .to_string();

        let dep_str = first_leg["departure"].as_str().unwrap();
        let arr_str = last_leg["arrival"].as_str().unwrap();
        let origin = first_leg["origin"]["name"].as_str().unwrap_or("").to_string();
        let destination = last_leg["destination"]["name"].as_str().unwrap_or("").to_string();

        let dep_dt = DateTime::parse_from_rfc3339(dep_str).unwrap().with_timezone(&Utc);
        let arr_dt = DateTime::parse_from_rfc3339(arr_str).unwrap().with_timezone(&Utc);

        let mut ferry_indices_in_window = Vec::new();
        for (idx, ferry) in ferry_map.iter().enumerate() {
            let parts: Vec<_> = ferry.ferry_dep.split(':').collect();
            let f_dt = Utc
                .with_ymd_and_hms(dep_dt.year(), dep_dt.month(), dep_dt.day(),
                                  parts[0].parse().unwrap(), parts[1].parse().unwrap(), 0)
                .unwrap();

            // Only include ferries within bus departure->arrival window minus min_travel
            if f_dt >= dep_dt && f_dt + min_travel <= arr_dt {
                ferry_indices_in_window.push(idx);
            }
        }

        // Assign buses to ferries in window, mark only the first ferry as first_possible
        for (i, &f_idx) in ferry_indices_in_window.iter().enumerate() {
            let assignment = BusAssignment {
                name: bus_name.clone(),
                origin: origin.clone(),
                destination: destination.clone(),
                dep: dep_dt.format("%H:%M").to_string(),
                arr: arr_dt.format("%H:%M").to_string(),
                first_possible: i == 0,
            };
            ferry_map[f_idx].buses.push(assignment);
        }
    }

    Ok(JsValue::from_serde(&ferry_map).unwrap())
}
