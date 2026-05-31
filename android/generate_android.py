import os

files = {
    # Gradle & Manifest
    "build.gradle.kts": """
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
    id("com.google.dagger.hilt.android") version "2.50" apply false
}
""",
    "app/build.gradle.kts": """
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
    id("com.google.dagger.hilt.android")
}

android {
    namespace = "com.clipforge"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.clipforge"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    
    // Navigation Compose
    implementation("androidx.navigation:navigation-compose:2.7.7")
    
    // Hilt
    implementation("com.google.dagger:hilt-android:2.50")
    kapt("com.google.dagger:hilt-android-compiler:2.50")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Coil
    implementation("io.coil-kt:coil-compose:2.5.0")
}
""",
    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.clipforge">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:name=".ClipForgeApp"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.ClipForge">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.ClipForge">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",
    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">ClipForge</string>
</resources>
""",
    "app/src/main/res/values/themes.xml": """<resources>
    <style name="Theme.ClipForge" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
""",

    # Application & Main Activity
    "app/src/main/java/com/clipforge/ClipForgeApp.kt": """package com.clipforge

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class ClipForgeApp : Application()
""",
    "app/src/main/java/com/clipforge/MainActivity.kt": """package com.clipforge

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.clipforge.presentation.navigation.AppNavGraph
import com.clipforge.presentation.theme.ClipForgeTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ClipForgeTheme {
                AppNavGraph()
            }
        }
    }
}
""",

    # Theme
    "app/src/main/java/com/clipforge/presentation/theme/Theme.kt": """package com.clipforge.presentation.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun ClipForgeTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        typography = Typography,
        content = content
    )
}
""",
    "app/src/main/java/com/clipforge/presentation/theme/Color.kt": """package com.clipforge.presentation.theme

import androidx.compose.ui.graphics.Color

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
""",
    "app/src/main/java/com/clipforge/presentation/theme/Type.kt": """package com.clipforge.presentation.theme

import androidx.compose.material3.Typography

val Typography = Typography()
""",

    # Navigation
    "app/src/main/java/com/clipforge/presentation/navigation/Screen.kt": """package com.clipforge.presentation.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Register : Screen("register")
    object Home : Screen("home")
    object ImportVideo : Screen("import_video")
    object AIClips : Screen("ai_clips")
    object Projects : Screen("projects")
    object Settings : Screen("settings")
    object Subscription : Screen("subscription")
}
""",
    "app/src/main/java/com/clipforge/presentation/navigation/AppNavGraph.kt": """package com.clipforge.presentation.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.clipforge.presentation.component.BottomNavigationBar
import com.clipforge.presentation.screen.auth.LoginScreen
import com.clipforge.presentation.screen.auth.RegisterScreen
import com.clipforge.presentation.screen.auth.SplashScreen
import com.clipforge.presentation.screen.clips.AIClipsScreen
import com.clipforge.presentation.screen.home.HomeScreen
import com.clipforge.presentation.screen.importvideo.ImportVideoScreen
import com.clipforge.presentation.screen.projects.ProjectsScreen
import com.clipforge.presentation.screen.settings.SettingsScreen
import com.clipforge.presentation.screen.subscription.SubscriptionScreen

@Composable
fun AppNavGraph() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    val showBottomNav = currentRoute in listOf(
        Screen.Home.route,
        Screen.AIClips.route,
        Screen.Projects.route,
        Screen.Settings.route
    )

    Scaffold(
        bottomBar = {
            if (showBottomNav) {
                BottomNavigationBar(navController = navController, currentRoute = currentRoute)
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Splash.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Splash.route) { SplashScreen(navController) }
            composable(Screen.Login.route) { LoginScreen(navController) }
            composable(Screen.Register.route) { RegisterScreen(navController) }
            composable(Screen.Home.route) { HomeScreen(navController) }
            composable(Screen.ImportVideo.route) { ImportVideoScreen(navController) }
            composable(Screen.AIClips.route) { AIClipsScreen(navController) }
            composable(Screen.Projects.route) { ProjectsScreen(navController) }
            composable(Screen.Settings.route) { SettingsScreen(navController) }
            composable(Screen.Subscription.route) { SubscriptionScreen(navController) }
        }
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/component/BottomNavigationBar.kt": """package com.clipforge.presentation.component

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.PlayArrow
import /* androidx.compose.material.icons.filled.Settings */ androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@Composable
fun BottomNavigationBar(navController: NavController, currentRoute: String?) {
    NavigationBar {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
            label = { Text("Home") },
            selected = currentRoute == Screen.Home.route,
            onClick = {
                navController.navigate(Screen.Home.route) {
                    popUpTo(Screen.Home.route) { inclusive = true }
                }
            }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.PlayArrow, contentDescription = "Clips") },
            label = { Text("Clips") },
            selected = currentRoute == Screen.AIClips.route,
            onClick = { navController.navigate(Screen.AIClips.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.List, contentDescription = "Projects") },
            label = { Text("Projects") },
            selected = currentRoute == Screen.Projects.route,
            onClick = { navController.navigate(Screen.Projects.route) }
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
            label = { Text("Settings") },
            selected = currentRoute == Screen.Settings.route,
            onClick = { navController.navigate(Screen.Settings.route) }
        )
    }
}
""",

    # Domain Models
    "app/src/main/java/com/clipforge/domain/model/User.kt": """package com.clipforge.domain.model

data class User(
    val id: String,
    val email: String,
    val fullName: String,
    val plan: String,
    val isPremium: Boolean = plan == "premium"
)
""",
    "app/src/main/java/com/clipforge/domain/model/Video.kt": """package com.clipforge.domain.model

data class Video(
    val id: String,
    val youtubeId: String,
    val title: String,
    val thumbnailUrl: String,
    val durationSeconds: Int,
    val status: String
)
""",
    "app/src/main/java/com/clipforge/domain/model/Clip.kt": """package com.clipforge.domain.model

data class Clip(
    val id: String,
    val videoId: String,
    val title: String,
    val clipType: String,
    val duration: Double,
    val hasWatermark: Boolean,
    val status: String
)
""",

    # States
    "app/src/main/java/com/clipforge/presentation/state/UIState.kt": """package com.clipforge.presentation.state

sealed class UIState<out T> {
    object Idle : UIState<Nothing>()
    object Loading : UIState<Nothing>()
    data class Success<T>(val data: T) : UIState<T>()
    data class Error(val message: String) : UIState<Nothing>()
}
""",

    # API & Repositories
    "app/src/main/java/com/clipforge/data/remote/api/AuthApi.kt": """package com.clipforge.data.remote.api

import com.clipforge.domain.model.User
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {
    @POST("auth/login")
    suspend fun login(@Body req: Map<String, String>): UserResponse

    @POST("auth/register")
    suspend fun register(@Body req: Map<String, String>): UserResponse

    @GET("auth/me")
    suspend fun getMe(): User
}

data class UserResponse(val user: User, val access_token: String)
""",
    "app/src/main/java/com/clipforge/data/remote/api/VideoApi.kt": """package com.clipforge.data.remote.api

import com.clipforge.domain.model.Video
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface VideoApi {
    @GET("videos")
    suspend fun getVideos(): VideoListResponse

    @POST("videos/import")
    suspend fun importVideo(@Body req: Map<String, String>): Video
}

data class VideoListResponse(val videos: List<Video>)
""",
    "app/src/main/java/com/clipforge/domain/repository/AuthRepository.kt": """package com.clipforge.domain.repository

import com.clipforge.domain.model.User
import kotlinx.coroutines.flow.Flow

interface AuthRepository {
    fun login(email: String, pass: String): Flow<Result<User>>
    fun register(email: String, pass: String, name: String): Flow<Result<User>>
    fun getMe(): Flow<Result<User>>
}
""",
    "app/src/main/java/com/clipforge/data/repository/AuthRepositoryImpl.kt": """package com.clipforge.data.repository

import com.clipforge.data.remote.api.AuthApi
import com.clipforge.domain.model.User
import com.clipforge.domain.repository.AuthRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val api: AuthApi
) : AuthRepository {
    override fun login(email: String, pass: String): Flow<Result<User>> = flow {
        try {
            val response = api.login(mapOf("email" to email, "password" to pass))
            emit(Result.success(response.user))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
    override fun register(email: String, pass: String, name: String): Flow<Result<User>> = flow {
        try {
            val response = api.register(mapOf("email" to email, "password" to pass, "full_name" to name))
            emit(Result.success(response.user))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
    override fun getMe(): Flow<Result<User>> = flow {
        try {
            emit(Result.success(api.getMe()))
        } catch (e: Exception) {
            emit(Result.failure(e))
        }
    }
}
""",

    # DI
    "app/src/main/java/com/clipforge/di/NetworkModule.kt": """package com.clipforge.di

import com.clipforge.data.remote.api.AuthApi
import com.clipforge.data.remote.api.VideoApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.clipforge.app/v1/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi = retrofit.create(AuthApi::class.java)

    @Provides
    @Singleton
    fun provideVideoApi(retrofit: Retrofit): VideoApi = retrofit.create(VideoApi::class.java)
}
""",
    "app/src/main/java/com/clipforge/di/RepositoryModule.kt": """package com.clipforge.di

import com.clipforge.data.repository.AuthRepositoryImpl
import com.clipforge.domain.repository.AuthRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindAuthRepository(
        impl: AuthRepositoryImpl
    ): AuthRepository
}
""",

    # ViewModels & Screens (Auth)
    "app/src/main/java/com/clipforge/presentation/screen/auth/AuthViewModel.kt": """package com.clipforge.presentation.screen.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.clipforge.domain.repository.AuthRepository
import com.clipforge.presentation.state.UIState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _loginState = MutableStateFlow<UIState<Unit>>(UIState.Idle)
    val loginState: StateFlow<UIState<Unit>> = _loginState

    fun login(email: String, pass: String) {
        _loginState.value = UIState.Loading
        viewModelScope.launch {
            authRepository.login(email, pass).collect { result ->
                if (result.isSuccess) {
                    _loginState.value = UIState.Success(Unit)
                } else {
                    _loginState.value = UIState.Error(result.exceptionOrNull()?.message ?: "Login Failed")
                }
            }
        }
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/auth/SplashScreen.kt": """package com.clipforge.presentation.screen.auth

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Text
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(navController: NavController) {
    LaunchedEffect(key1 = true) {
        delay(1500)
        navController.navigate(Screen.Login.route) {
            popUpTo(Screen.Splash.route) { inclusive = true }
        }
    }
    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("CLIPFORGE", style = MaterialTheme.typography.headlineLarge, color = MaterialTheme.colorScheme.primary)
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/auth/LoginScreen.kt": """package com.clipforge.presentation.screen.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen
import com.clipforge.presentation.state.UIState

@Composable
fun LoginScreen(navController: NavController, viewModel: AuthViewModel = hiltViewModel()) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val loginState by viewModel.loginState.collectAsState()

    LaunchedEffect(loginState) {
        if (loginState is UIState.Success) {
            navController.navigate(Screen.Home.route) {
                popUpTo(Screen.Login.route) { inclusive = true }
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Login to ClipForge", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedTextField(value = email, onValueChange = { email = it }, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(value = password, onValueChange = { password = it }, label = { Text("Password") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(16.dp))
        
        if (loginState is UIState.Loading) {
            CircularProgressIndicator()
        } else {
            Button(onClick = { viewModel.login(email, password) }, modifier = Modifier.fillMaxWidth()) {
                Text("Login")
            }
        }
        
        if (loginState is UIState.Error) {
            Text((loginState as UIState.Error).message, color = MaterialTheme.colorScheme.error)
        }
        
        TextButton(onClick = { navController.navigate(Screen.Register.route) }) {
            Text("Don't have an account? Register")
        }
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/auth/RegisterScreen.kt": """package com.clipforge.presentation.screen.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@Composable
fun RegisterScreen(navController: NavController) {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Register", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedTextField(value = "", onValueChange = {}, label = { Text("Full Name") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(value = "", onValueChange = {}, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(value = "", onValueChange = {}, label = { Text("Password") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(16.dp))
        
        Button(onClick = { /* TODO */ }, modifier = Modifier.fillMaxWidth()) {
            Text("Register")
        }
        TextButton(onClick = { navController.popBackStack() }) {
            Text("Back to Login")
        }
    }
}
""",

    # Main Screens
    "app/src/main/java/com/clipforge/presentation/screen/home/HomeScreen.kt": """package com.clipforge.presentation.screen.home

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.clipforge.presentation.navigation.Screen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(navController: NavController) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("ClipForge") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { navController.navigate(Screen.ImportVideo.route) }) {
                Icon(Icons.Default.Add, contentDescription = "Import Video")
            }
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text("Welcome back!", style = MaterialTheme.typography.headlineSmall)
            Spacer(modifier = Modifier.height(16.dp))
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Today's Stats", style = MaterialTheme.typography.titleMedium)
                    Text("0 Videos Imported")
                    Text("0 Clips Created")
                }
            }
        }
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/importvideo/ImportVideoScreen.kt": """package com.clipforge.presentation.screen.importvideo

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImportVideoScreen(navController: NavController) {
    var url by remember { mutableStateOf("") }
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Import Video") })
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            OutlinedTextField(
                value = url,
                onValueChange = { url = it },
                label = { Text("YouTube URL") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = { /* TODO Import */ }, modifier = Modifier.fillMaxWidth()) {
                Text("Get Video Info")
            }
        }
    }
}
""",
    "app/src/main/java/com/clipforge/presentation/screen/clips/AIClipsScreen.kt": """package com.clipforge.presentation.screen.clips

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
""",
    "app/src/main/java/com/clipforge/presentation/screen/projects/ProjectsScreen.kt": """package com.clipforge.presentation.screen.projects

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
""",
    "app/src/main/java/com/clipforge/presentation/screen/settings/SettingsScreen.kt": """package com.clipforge.presentation.screen.settings

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
""",
    "app/src/main/java/com/clipforge/presentation/screen/subscription/SubscriptionScreen.kt": """package com.clipforge.presentation.screen.subscription

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
"""
}

for path, content in files.items():
    full_path = os.path.join("/sdcard/ClipForge/android", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Android files generated successfully.")
