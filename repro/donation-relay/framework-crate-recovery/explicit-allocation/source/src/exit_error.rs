//! Program-specific error constructors over the reconstructed framework crate.
pub use relay_error_model_reconstructed::*;
use std::fmt::{Display, Formatter};

// The admitted account conversion roles share the owned framework model.
// Keep the owned name and Display-to-String construction of the framework
// conversion; do not replace the message with a borrowed catalog reference.
enum AccountErrorCode { AccountDiscriminatorNotFound, AccountDidNotDeserialize, AccountDidNotSerialize }
impl AccountErrorCode {
    fn name(&self) -> String {
        match self {
            Self::AccountDiscriminatorNotFound => "AccountDiscriminatorNotFound".to_owned(),
            Self::AccountDidNotDeserialize => "AccountDidNotDeserialize".to_owned(),
            Self::AccountDidNotSerialize => "AccountDidNotSerialize".to_owned(),
        }
    }
}
impl Display for AccountErrorCode {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::AccountDiscriminatorNotFound => f.write_str("No discriminator was found on the account"),
            Self::AccountDidNotDeserialize => f.write_str("Failed to deserialize the account"),
            Self::AccountDidNotSerialize => f.write_str("Failed to serialize the account"),
        }
    }
}
pub fn account_did_not_serialize() -> Error {
    account_io_error(AccountErrorCode::AccountDidNotSerialize)
}
pub fn account_did_not_deserialize() -> Error {
    account_io_error(AccountErrorCode::AccountDidNotDeserialize)
}
pub fn account_discriminator_not_found() -> Error {
    account_io_error(AccountErrorCode::AccountDiscriminatorNotFound)
}
fn account_io_error(code: AccountErrorCode) -> Error {
    AnchorError {
        error_name: code.name(),
        error_code_number: match &code {
            AccountErrorCode::AccountDiscriminatorNotFound => 3001,
            AccountErrorCode::AccountDidNotDeserialize => 3003,
            AccountErrorCode::AccountDidNotSerialize => 3004,
        },
        error_msg: code.to_string(),
        error_origin: None,
        compared_values: None,
    }.into()
}

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
struct AccountDiscriminatorMismatch;
impl Display for AccountDiscriminatorMismatch {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str("Account discriminator did not match what was expected")
    }
}
pub(crate) fn account_discriminator_mismatch() -> Error {
    let error_name = "AccountDiscriminatorMismatch".to_owned();
    let error_msg = AccountDiscriminatorMismatch.to_string();
    AnchorError {
        error_name,
        error_code_number: 3002,
        error_msg,
        error_origin: Some(ErrorOrigin::Source(Source {
            filename: "programs/contracts/src/lib.rs",
            line: 36,
        })),
        compared_values: None,
    }.into()
}
