//! MESIE Reality Capsula — Rust φ-kernel for design scores and spectral ops.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::{self, Read};

const PHI: f64 = 0.618_033_988_749_894_8;

#[derive(Debug, Deserialize)]
struct Request {
    action: String,
    seed: Option<f64>,
    record: Option<Value>,
    record_a: Option<Value>,
    record_b: Option<Value>,
}

#[derive(Debug, Serialize)]
struct Response {
    ok: bool,
    data: Value,
    runtime: &'static str,
    error: Option<String>,
}

pub fn phi_design_score(seed: f64) -> f64 {
    let s = seed.clamp(0.0, 1.0);
    (s * PHI + (1.0 - PHI) * 0.5).clamp(0.0, 1.0)
}

pub fn phi_fingerprint(n: usize) -> Vec<f64> {
    (0..n.min(8))
        .map(|i| {
            let score = phi_design_score(i as f64 / n.max(1) as f64);
            (score * (i as f64 * PHI).cos()).round() * 1_000_000.0 / 1_000_000.0
        })
        .collect()
}

fn primary_arrays(record: &Value) -> (Vec<f64>, Vec<f64>) {
    if let Some(comps) = record.get("components").and_then(|c| c.as_array()) {
        if let Some(c0) = comps.first() {
            let f = c0["frequency"].as_array().cloned().unwrap_or_default();
            let a = c0["amplitude"].as_array().cloned().unwrap_or_default();
            return (
                f.iter().filter_map(|x| x.as_f64()).collect(),
                a.iter().filter_map(|x| x.as_f64()).collect(),
            );
        }
    }
    let f = record["frequency"].as_array().cloned().unwrap_or_default();
    let a = record["amplitude"].as_array().cloned().unwrap_or_default();
    (
        f.iter().filter_map(|x| x.as_f64()).collect(),
        a.iter().filter_map(|x| x.as_f64()).collect(),
    )
}

fn validate(record: &Value) -> Value {
    let (freq, amp) = primary_arrays(record);
    let mut errors = vec![];
    if freq.is_empty() || amp.is_empty() {
        errors.push("missing frequency/amplitude");
    }
    if freq.len() != amp.len() {
        errors.push("length mismatch");
    }
    serde_json::json!({
        "is_valid": errors.is_empty(),
        "level": if errors.is_empty() { 5 } else { 2 },
        "errors": errors,
        "phi_score": phi_design_score(freq.len() as f64 / 64.0),
        "runtime": "capsula-rust"
    })
}

fn cosine(a: &[f64], b: &[f64]) -> f64 {
    let n = a.len().min(b.len());
    if n == 0 {
        return 0.0;
    }
    let dot: f64 = a[..n].iter().zip(&b[..n]).map(|(x, y)| x * y).sum();
    let na: f64 = a[..n].iter().map(|x| x * x).sum::<f64>().sqrt();
    let nb: f64 = b[..n].iter().map(|x| x * x).sum::<f64>().sqrt();
    if na < 1e-12 || nb < 1e-12 {
        return 0.0;
    }
    dot / (na * nb)
}

fn match_records(a: &Value, b: &Value) -> Value {
    let (_, aa) = primary_arrays(a);
    let (_, ab) = primary_arrays(b);
    let c = cosine(&aa, &ab);
    let score = (0.6 * c + 0.4 * phi_design_score(c)).clamp(0.0, 1.0);
    serde_json::json!({
        "composite_score": score,
        "metrics": { "cosine": c },
        "fingerprint": phi_fingerprint(8),
        "runtime": "capsula-rust"
    })
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap_or_default();
    let req: Request = serde_json::from_str(&input).unwrap_or(Request {
        action: "health".into(),
        seed: None,
        record: None,
        record_a: None,
        record_b: None,
    });

    let (ok, data, error) = match req.action.as_str() {
        "health" => (
            true,
            serde_json::json!({"status": "ok", "phi": PHI}),
            None,
        ),
        "phi_score" => {
            let seed = req.seed.unwrap_or(0.618);
            (
                true,
                serde_json::json!({
                    "score": phi_design_score(seed),
                    "fingerprint": phi_fingerprint(8),
                    "phi": PHI
                }),
                None,
            )
        }
        "validate" => (true, validate(&req.record.unwrap_or(Value::Null)), None),
        "match" => {
            let a = req.record_a.or(req.record).unwrap_or(Value::Null);
            let b = req.record_b.unwrap_or(Value::Null);
            (true, match_records(&a, &b), None)
        }
        other => (
            false,
            Value::Null,
            Some(format!("unsupported action: {other}")),
        ),
    };

    let resp = Response {
        ok,
        data,
        runtime: "capsula-rust",
        error,
    };
    println!("{}", serde_json::to_string(&resp).unwrap());
}
