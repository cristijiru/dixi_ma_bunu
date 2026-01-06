use actix_web::{test, web, App};
use dixi_backend::routes;

#[actix_web::test]
async fn test_health_endpoint() {
    let app = test::init_service(
        App::new().configure(routes::configure_health_only)
    ).await;

    let req = test::TestRequest::get().uri("/api/health").to_request();
    let resp = test::call_service(&app, req).await;

    assert!(resp.status().is_success());
}

#[actix_web::test]
async fn test_health_returns_ok_status() {
    let app = test::init_service(
        App::new().configure(routes::configure_health_only)
    ).await;

    let req = test::TestRequest::get().uri("/api/health").to_request();
    let resp: serde_json::Value = test::call_and_read_body_json(&app, req).await;

    assert_eq!(resp["status"], "ok");
}
