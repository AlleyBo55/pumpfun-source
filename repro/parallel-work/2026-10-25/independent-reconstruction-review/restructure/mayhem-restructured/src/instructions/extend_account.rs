use anchor_lang::prelude::*;
use crate::*;
use crate::state::*;
use crate::checked_program::*;
use anchor_spl::{associated_token::AssociatedToken, token_interface::{Mint, TokenAccount, TokenInterface}};

pub fn extend_account(ctx: Context<ExtendAccount>) -> Result<()> {
        let account = ctx.accounts.account.to_account_info();
        let old_size = account.data_len();
        let new_size = {
            let data = account.try_borrow_data()?;
            match data.get(..8) {
                Some(d) if d == GlobalParams::DISCRIMINATOR => 318,
                Some(d) if d == FeeRecipient::DISCRIMINATOR => 74,
                Some(d) if d == [0xb1,0xfd,0xbf,0x7d,0xcb,0x16,0x86,0x6b] => 170,
                _ => return err!(MayhemError::AccountTypeNotSupported),
            }
        };
        if old_size == new_size {
            msg!("Account already has the correct size");
            return Ok(());
        }
        if old_size > new_size {
            msg!("Account already has more than {} bytes: {}", new_size, old_size);
            return Ok(());
        }
        let required = Rent::get()?.minimum_balance(new_size).saturating_sub(account.lamports());
        if required > 0 {
            anchor_lang::system_program::transfer(
                CpiContext::new(ctx.accounts.system_program.key(),
                    anchor_lang::system_program::Transfer {
                        from: ctx.accounts.user.to_account_info(), to: account.clone()
                    }), required)?;
        }
        account.resize(new_size)?;
        let event = ExtendAccountEvent {
            account: account.key(), user: ctx.accounts.user.key(),
            old_size: old_size as u64, new_size: new_size as u64,
            timestamp: Clock::get()?.unix_timestamp,
        };
        emit!(event);
        emit_cpi!(event);
        Ok(())
    }
