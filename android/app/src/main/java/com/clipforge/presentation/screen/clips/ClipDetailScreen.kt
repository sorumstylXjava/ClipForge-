package com.clipforge.presentation.screen.clips

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ClipDetailScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Clip Detail") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Video Player
            }
            Spacer(modifier = Modifier.height(16.dp))
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer), modifier = Modifier.fillMaxWidth()) {
                Text("⚠ [Free] This clip has a ClipForge watermark", modifier = Modifier.padding(8.dp))
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Clip Title", style = MaterialTheme.typography.titleLarge)
            Text("00:30 → 01:15 (45 sec) • 720p • 10.2MB")
            Spacer(modifier = Modifier.height(24.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
                Button(onClick = { /* Download */ }) { Text("Download") }
                OutlinedButton(onClick = { /* Share */ }) { Text("Share") }
            }
            Spacer(modifier = Modifier.height(16.dp))
            TextButton(onClick = { /* Delete */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Delete Clip", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}
