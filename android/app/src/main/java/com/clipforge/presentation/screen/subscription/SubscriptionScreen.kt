package com.clipforge.presentation.screen.subscription

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SubscriptionScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("ClipForge Premium") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Premium Plan", style = MaterialTheme.typography.titleLarge)
                    Text("Unlock all AI features, 4K export, and remove watermarks.")
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { /* TODO payment */ }, modifier = Modifier.fillMaxWidth()) {
                        Text("Upgrade Now")
                    }
                }
            }
        }
    }
}
