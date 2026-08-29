workspace "Dependency Check Fixture" "Fixture project with one forbidden dependency" {

    properties {
        "arc42.projected" "false"
    }

    model {
        module_a must_not_depend_on module_b
        conforming must_not_depend_on module_b
    }
}
