package com.clipforge.presentation.screen.projects

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProjectsScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Projects") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            Text("Your imported videos will appear here.")
        }
    }
}
