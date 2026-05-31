package com.clipforge.presentation.screen.settings

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(navController: NavController) {
    Scaffold(
        topBar = { TopAppBar(title = { Text("Settings") }) }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Button(onClick = { navController.navigate(Screen.Subscription.route) }, modifier = Modifier.fillMaxWidth()) {
                Text("Manage Subscription")
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = {
                navController.navigate(Screen.Login.route) {
                    popUpTo(0)
                }
            }, modifier = Modifier.fillMaxWidth(), colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)) {
                Text("Logout")
            }
        }
    }
}
