package com.clipforge.presentation.component

import androidx.compose.material3.*
import androidx.compose.runtime.Composable

@Composable
fun DailyLimitDialog(onDismiss: () -> Unit, onUpgrade: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("🔒 Daily Limit Reached") },
        text = { 
            Text("You have imported 3/3 videos today.\nResets at 00:00.\n\nUpgrade to Premium for unlimited imports.")
        },
        confirmButton = {
            Button(onClick = onUpgrade) {
                Text("Upgrade Premium")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Come back tomorrow")
            }
        }
    )
}
