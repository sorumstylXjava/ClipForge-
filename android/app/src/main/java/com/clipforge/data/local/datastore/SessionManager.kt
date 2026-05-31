package com.clipforge.data.local.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "session_prefs")

@Singleton
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    companion object {
        val ACCESS_TOKEN = stringPreferencesKey("access_token")
        val USER_ID = stringPreferencesKey("user_id")
        val CURRENT_PLAN = stringPreferencesKey("current_plan")
    }

    val accessTokenFlow: Flow<String?> = context.dataStore.data.map { preferences ->
        preferences[ACCESS_TOKEN]
    }

    val userIdFlow: Flow<String?> = context.dataStore.data.map { preferences ->
        preferences[USER_ID]
    }

    val currentPlanFlow: Flow<String?> = context.dataStore.data.map { preferences ->
        preferences[CURRENT_PLAN]
    }

    suspend fun saveSession(token: String, id: String, plan: String) {
        context.dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN] = token
            preferences[USER_ID] = id
            preferences[CURRENT_PLAN] = plan
        }
    }

    suspend fun clearSession() {
        context.dataStore.edit { preferences ->
            preferences.remove(ACCESS_TOKEN)
            preferences.remove(USER_ID)
            preferences.remove(CURRENT_PLAN)
        }
    }
}
