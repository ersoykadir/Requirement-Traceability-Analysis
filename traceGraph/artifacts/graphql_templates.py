"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

This file contains github graphql query templates for each artifact type.
"""

from string import Template

REQ_queryTemplate = Template("""{
    repository(owner:"bounswe", name:"bounswe2022group2") {
        createdAt
    }
}
""")
ISSUE_queryTemplate = Template("""{
    repository(owner:"$owner", name:"$name") {
        issues(first: 100, after:$cursor) {
            totalCount
            nodes{
                url
                title
                number
                body
                createdAt 
                closedAt
                state
                milestone{
                    title
                    description
                    number
                }
                comments(first:100){
                    totalCount
                    nodes{
                        body
                    }
                }
            }
            pageInfo{
                endCursor
                hasNextPage
            }
        }
    }
}""")
PR_queryTemplate = Template("""{
    repository(owner:"$owner", name:"$name") {
        pullRequests(first:100, after:$cursor) {
            nodes{
                url
                title
                number
                body
                createdAt 
                closedAt
                state
                milestone{
                    title
                    description
                    number
                }
                comments(first:100){
                    totalCount
                    nodes{
                        body
                    }
                }
                commits(first:100){
                    totalCount
                    nodes{
                        commit{
                            oid
                            message
                            url
                            committedDate
                        }
                    }
                }
            }
            pageInfo{
                endCursor
                hasNextPage
            }
        }
    }
}""")
COMMIT_queryTemplate = Template("""{
    repository(owner: "$owner", name: "$name") {
        ref(qualifiedName: "master") {
            target {
                ... on Commit {
                    history(first: 100, after:$cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes{
                        oid
                        message
                        committedDate
                        url
                        associatedPullRequests(first:10){
                            nodes{
                                number
                            }
                        }
                        }
                    }
                }
            }
        }
    }
}""")