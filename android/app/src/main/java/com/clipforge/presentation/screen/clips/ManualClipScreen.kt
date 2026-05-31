package com.clipforge.presentation.screen.clips

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManualClipScreen(navController: NavController) {
    var title by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Manual Clip") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Card(modifier = Modifier.fillMaxWidth().height(200.dp)) {
                // Video Player Placeholder
            }
            Spacer(modifier = Modifier.height(16.dp))
            Text("Start Time: 00:00:30")
            Text("End Time: 00:01:30")
            Text("Duration: 1 min 0 sec")
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Clip Title (optional)") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { navController.navigate(Screen.ClipDetail.createRoute("new_clip")) }, modifier = Modifier.fillMaxWidth()) {
                Text("Create Clip")
            }
        }
    }
}
