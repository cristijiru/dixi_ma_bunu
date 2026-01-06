use actix_web::{test, App};
use dixi_backend::routes;

#[actix_web::test]
async fn test_health_endpoint_returns_200() {
    let app = test::init_service(
        App::new().configure(routes::configure_health_only)
    ).await;

    let req = test::TestRequest::get().uri("/api/health").to_request();
    let resp = test::call_service(&app, req).await;

    assert!(resp.status().is_success());
}

#[actix_web::test]
async fn test_health_endpoint_returns_ok_status() {
    let app = test::init_service(
        App::new().configure(routes::configure_health_only)
    ).await;

    let req = test::TestRequest::get().uri("/api/health").to_request();
    let resp: serde_json::Value = test::call_and_read_body_json(&app, req).await;

    assert_eq!(resp["status"], "ok");
}

#[actix_web::test]
async fn test_health_endpoint_json_content_type() {
    let app = test::init_service(
        App::new().configure(routes::configure_health_only)
    ).await;

    let req = test::TestRequest::get().uri("/api/health").to_request();
    let resp = test::call_service(&app, req).await;

    let content_type = resp.headers().get("content-type").unwrap();
    assert!(content_type.to_str().unwrap().contains("application/json"));
}
