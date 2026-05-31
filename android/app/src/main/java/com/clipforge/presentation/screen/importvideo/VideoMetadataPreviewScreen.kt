package com.clipforge.presentation.screen.importvideo

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoMetadataPreviewScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Preview Video") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Placeholder for Video Thumbnail
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Video Title", style = MaterialTheme.typography.titleLarge)
            Text("Channel Name • 03:32 • 1080p", style = MaterialTheme.typography.bodyMedium)
            
            Spacer(modifier = Modifier.height(32.dp))
            Button(onClick = { navController.navigate(Screen.ClipOptions.createRoute("sample_video_id")) }, modifier = Modifier.fillMaxWidth()) {
                Text("Import & Choose Action")
            }
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedButton(onClick = { navController.popBackStack() }, modifier = Modifier.fillMaxWidth()) {
                Text("Cancel")
            }
        }
    }
}
