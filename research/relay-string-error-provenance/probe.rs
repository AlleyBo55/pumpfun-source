#![crate_type = "lib"]
#[no_mangle]
pub fn io_error_type_id() -> std::any::TypeId {
    std::any::TypeId::of::<std::io::Error>()
}
#[no_mangle]
pub fn boxed_string_error() -> Box<dyn std::error::Error + Send + Sync> {
    String::from("relay probe").into()
}
