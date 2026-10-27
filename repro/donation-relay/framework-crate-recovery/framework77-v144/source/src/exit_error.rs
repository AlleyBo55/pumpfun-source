//! Program-specific error constructors over the reconstructed framework crate.
pub use relay_error_model_reconstructed::*;
use std::fmt::{Display, Formatter};

// Real framework enum variants cross the reconstructed dependency boundary.
pub fn account_did_not_serialize() -> Error { ErrorCode::AccountDidNotSerialize.into() }
pub fn account_did_not_deserialize() -> Error { ErrorCode::AccountDidNotDeserialize.into() }
pub fn account_discriminator_not_found() -> Error { ErrorCode::AccountDiscriminatorNotFound.into() }

// Reconstructed program diagnostic data, decoded from the captured error6009
// constructor. These values describe that program's Source object; they do not
// assert that this independently written Rust file occupied the original path.
struct InvalidMessageLength;
impl Display for InvalidMessageLength {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("Invalid message length")
    }
}
pub(crate) fn invalid_message_length() -> Error {
    let error_name = "InvalidMessageLength".to_owned();
    let error_msg = InvalidMessageLength.to_string();
    AnchorError {
        error_name,
        error_code_number: 6009,
        error_msg,
        error_origin: Some(ErrorOrigin::Source(Source {
            filename: "programs/contracts/src/tools/checks.rs",
            line: 55,
        })),
        compared_values: None,
    }.into()
}

struct InvalidBps;
impl Display for InvalidBps {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("Invalid bps")
    }
}
pub(crate) fn invalid_bps() -> Error {
    let error_name = "InvalidBps".to_owned();
    let error_msg = InvalidBps.to_string();
    AnchorError {
        error_name,
        error_code_number: 6018,
        error_msg,
        error_origin: Some(ErrorOrigin::Source(Source {
            filename: "programs/contracts/src/tools/checks.rs",
            line: 192,
        })),
        compared_values: None,
    }.into()
}

// The checked IDL header constructs Source before boxing, then replaces it
// with an allocated IdlAccount name. The outer parser replaces that name again.
pub(crate) fn account_discriminator_mismatch() -> Error {
    let code = ErrorCode::AccountDiscriminatorMismatch;
    AnchorError {
        error_name: code.name(),
        error_code_number: code.into(),
        error_msg: code.to_string(),
        error_origin: Some(ErrorOrigin::Source(Source {
            filename: "programs/contracts/src/lib.rs",
            line: 36,
        })),
        compared_values: None,
    }.into()
}
