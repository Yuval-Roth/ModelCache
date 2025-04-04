
import ModelCacheRequest.*
import utils.JsonUtils
import utils.RestApiClient
import utils.toJson

const val URL = "http://localhost:5000/modelcache"

fun main() {
    while(true){
        println("Select an option:")
        println("1. Insert to cache")
        println("2. Query cache")
        println("3. Clear cache")
        println("4. Exit")
        print(">> ")
        val choice = readlnOrNull() ?: continue
        when (choice) {
            "1" -> {
                val chatInfo = mutableListOf<Query>()
                while(true){
                    val entries = getQueryEntries()
                    println("Enter output:")
                    print(">> ")
                    val output = readlnOrNull()
                    if (output.isNullOrBlank()) {
                        println("Output cannot be empty. Please try again.")
                        continue
                    }
                    chatInfo.add(Query(entries, output))
                    println("Do you want to add more entries? (y/n)")
                    print(">> ")
                    val addMore = readlnOrNull()
                    if (addMore.equals("n", ignoreCase = true)) {
                        break
                    } else if (!addMore.equals("y", ignoreCase = true)) {
                        println("Invalid choice. Please try again.")
                        continue
                    }
                }
                println()
                println("Inserting to cache...")
                println("Response: ${insertToCache(chatInfo)}")
                println()
            }
            "2" -> {
                val entries = getQueryEntries()
                println()
                println("Querying cache...")
                println("Response: ${queryCache(entries)}")
                println()
            }
            "3" -> {
                val response = clearCache()
                println()
                println("Clearing cache...")
                println("Response: $response")
                println()
            }
            "4" -> {
                println()
                println("Exiting...")
                return
            }
            else -> {
                println()
                println("Invalid choice. Please try again.")
                println()
            }
        }
    }

}

private fun getQueryEntries(): MutableList<QueryEntry> {
    println("Enter input data\n")
    val entries = mutableListOf<QueryEntry>()
    var firstTime = true
    while (true) {
        println("Role:")
        println("1. User")
        println("2. System")
        if(! firstTime) println("3. Done")
        print(">> ")
        val roleChoice = readlnOrNull() ?: continue
        when (roleChoice) {
            "1", "2" -> {
                firstTime = false
            }
            "3" -> {
                if(!firstTime) {
                    break
                } else {
                    println("Invalid choice. Please try again.")
                    continue
                }
            }
            else -> {
                println("Invalid choice. Please try again.")
                continue
            }
        }
        println("Enter message:")
        print(">> ")
        val message = readlnOrNull()
        if (message.isNullOrBlank()) {
            println("Message cannot be empty. Please try again.")
            continue
        }
        entries.add(QueryEntry(Role.entries[roleChoice.toInt() - 1], message))
        println()
    }
    return entries
}

// ===================================================================== |
// ===================== ModelCache API operations ===================== |
// ===================================================================== |

fun insertToCache(chatInfo: List<Query>): String {
    val request = ModelCacheRequest(
        type = Type.INSERT,
        chatInfo = chatInfo
    )
    return sendRequest(request)
}

fun queryCache(query: List<QueryEntry>): String {
    val request = ModelCacheRequest(
        type = Type.QUERY,
        query = query
    )
    return sendRequest(request)
}

fun clearCache(): String {
    val request = ModelCacheRequest(
        type = Type.REMOVE,
        removeType = RemoveType.TRUNCATE_BY_MODEL
    )
    return sendRequest(request)
}

fun sendRequest(request: ModelCacheRequest): String {
    // NOTE:
    // Serialization is done twice here because the ModelCache backend
    // deserializes the request twice for some reason
    val body = JsonUtils.serialize(request.toJson(),true)

    val response = RestApiClient()
        .withUri(URL)
        .withHeader("Content-Type", "application/json")
        .withBody(body)
        .withPost()
        .send()
    return response
}