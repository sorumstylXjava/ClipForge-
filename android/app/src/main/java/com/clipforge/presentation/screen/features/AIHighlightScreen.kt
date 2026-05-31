package com.clipforge.presentation.screen.features

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIHighlightScreen(navController: NavController) {
    var maxHighlights by remember { mutableStateOf(5f) }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("AI Highlight Detection") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Max Highlights: ${maxHighlights.toInt()}")
            Slider(value = maxHighlights, onValueChange = { maxHighlights = it }, valueRange = 1f..10f, steps = 8)
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = { /* Start Job */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Start Analysis")
            }
        }
    }
}
