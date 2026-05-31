package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SpeechSearchScreen(navController: NavController) {
    var query by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Speech Search (Premium)") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text("Search word or phrase") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Search & Auto-Clip")
            }
        }
    }
}
