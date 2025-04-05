import com.google.gson.annotations.SerializedName

data class ModelCacheRequest(
    // Mandatory fields
    val type: Type,
    val scope: Scope = Scope(Model.CODEGPT_1008), // I don't know if this is the only available option,
                                                    // but it seems like it is, so it's defaulted to this for now
    // Used for inserting
    @SerializedName("chat_info")
    val chatInfo: List<Query>? = null,

    // Used for querying
    val query: List<QueryEntry>? = null,

    // Used for removing
    @SerializedName("remove_type")
    val removeType: RemoveType? = null,
) {

    /**
     * Type of the ModelCache operation.
     */
    enum class Type {
        @SerializedName("insert")  INSERT,
        @SerializedName("query")   QUERY,
        @SerializedName("remove")  REMOVE
    }

    enum class Model {
        @SerializedName("CODEGPT-1008")  CODEGPT_1008;
    }

    /**
     * Type of removal operation.
     */
    enum class RemoveType {
        @SerializedName("truncate_by_model")  TRUNCATE_BY_MODEL,
    }

    /**
     * Role of the actor in the conversation.
     */
    enum class Role {
        @SerializedName("user")    USER,
        @SerializedName("system")  SYSTEM,
    }

    data class Scope(val model: Model)

    data class QueryEntry(
        val role: Role,
        val content: String,
    )

    data class Query(
        val query: List<QueryEntry>,
        val answer: String,
    )
}