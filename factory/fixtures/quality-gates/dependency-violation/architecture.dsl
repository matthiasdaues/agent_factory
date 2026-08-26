workspace "Dependency Check Fixture" "Fixture project with one forbidden dependency" {
    model {
        module_a must_not_depend_on module_b
        conforming must_not_depend_on module_b
    }
}
