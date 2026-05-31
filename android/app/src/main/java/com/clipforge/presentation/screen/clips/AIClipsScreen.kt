package com.clipforge.presentation.screen.clips

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIClipsScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("AI Clips") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            Text("Your generated clips will appear here.")
        }
    }
}
