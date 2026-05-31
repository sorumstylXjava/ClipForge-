package com.clipforge.presentation.component

import androidx.compose.material3.*
import androidx.compose.runtime.Composable

@Composable
fun PremiumGateDialog(featureName: String, onDismiss: () -> Unit, onUpgrade: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("⭐ Premium Feature") },
        text = { 
            Text("$featureName is available in ClipForge Premium.\n\n✓ Unlimited videos\n✓ 4K Export\n✓ No Watermark\n✓ All AI Tracking Features")
        },
        confirmButton = {
            Button(onClick = onUpgrade) {
                Text("Upgrade Now")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Later")
            }
        }
    )
}
