package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ObjectTrackingScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Object Tracking (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Select objects to track (e.g. Person, Car, Cat)")
            // Checkboxes placeholder
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Tracking")
            }
        }
    }
}
