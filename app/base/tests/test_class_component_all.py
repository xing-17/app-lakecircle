"""Comprehensive tests for Component class."""

from __future__ import annotations

from unittest.mock import Mock

from xlog.format import FormatLike, Text
from xlog.group.loggroup import LogGroup
from xlog.stream import LogStream

from app.base.component import Component


class TestComponentInitialization:
    """Test Component initialization."""

    def test_init_minimal(self):
        """Test initialization with minimal arguments."""
        component = Component(name="test-component")

        assert component.name == "test-component"
        assert component.level == "INFO"
        assert isinstance(component.logformat, Text)
        assert component.loggroup is None
        assert isinstance(component.logstream, LogStream)

    def test_init_with_level(self):
        """Test initialization with custom level."""
        component = Component(name="test", level="DEBUG")

        assert component.level == "DEBUG"

    def test_init_with_lowercase_level(self):
        """Test initialization with lowercase level converts to uppercase."""
        component = Component(name="test", level="warning")

        assert component.level == "WARNING"

    def test_init_with_logformat(self):
        """Test initialization with custom log format."""
        custom_format = Mock(spec=FormatLike)
        component = Component(name="test", logformat=custom_format)

        assert component.logformat is custom_format

    def test_init_with_loggroup(self):
        """Test initialization with log group."""
        loggroup = Mock(spec=LogGroup)
        component = Component(name="test", loggroup=loggroup)

        assert component.loggroup is loggroup

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        custom_format = Mock(spec=FormatLike)
        loggroup = Mock(spec=LogGroup)

        component = Component(
            name="full-test",
            level="ERROR",
            logformat=custom_format,
            loggroup=loggroup,
        )

        assert component.name == "full-test"
        assert component.level == "ERROR"
        assert component.logformat is custom_format
        assert component.loggroup is loggroup


class TestComponentResolveLevel:
    """Test _resolve_level method."""

    def test_resolve_level_uppercase(self):
        """Test resolve level returns uppercase."""
        component = Component(name="test")

        result = component._resolve_level("info")

        assert result == "INFO"

    def test_resolve_level_already_uppercase(self):
        """Test resolve level with already uppercase input."""
        component = Component(name="test")

        result = component._resolve_level("DEBUG")

        assert result == "DEBUG"

    def test_resolve_level_empty_string(self):
        """Test resolve level with empty string returns default."""
        component = Component(name="test")

        result = component._resolve_level("")

        assert result == "INFO"

    def test_resolve_level_none(self):
        """Test resolve level with None returns default."""
        component = Component(name="test")

        result = component._resolve_level(None)

        assert result == "INFO"


class TestComponentResolveLogFormat:
    """Test _resolve_logformat method."""

    def test_resolve_logformat_none(self):
        """Test resolve logformat with None returns Text."""
        component = Component(name="test")

        result = component._resolve_logformat(None)

        assert isinstance(result, Text)

    def test_resolve_logformat_custom(self):
        """Test resolve logformat with custom format."""
        component = Component(name="test")
        custom_format = Mock(spec=FormatLike)

        result = component._resolve_logformat(custom_format)

        assert result is custom_format


class TestComponentResolveLogGroup:
    """Test _resolve_loggroup method."""

    def test_resolve_loggroup_none(self):
        """Test resolve loggroup with None."""
        component = Component(name="test")

        result = component._resolve_loggroup(None)

        assert result is None

    def test_resolve_loggroup_with_group(self):
        """Test resolve loggroup with group."""
        component = Component(name="test")
        loggroup = Mock(spec=LogGroup)

        result = component._resolve_loggroup(loggroup)

        assert result is loggroup


class TestComponentResolveLogStream:
    """Test _resolve_logstream method."""

    def test_resolve_logstream_no_loggroup(self):
        """Test resolve logstream without loggroup."""
        component = Component(name="test", level="INFO")

        logstream = component._resolve_logstream()

        assert isinstance(logstream, LogStream)
        assert logstream.name == "test::stream"
        assert logstream.level == "INFO"
        assert logstream.verbose is True

    def test_resolve_logstream_with_loggroup(self):
        """Test resolve logstream with loggroup."""
        loggroup = Mock(spec=LogGroup)
        component = Component(name="test", loggroup=loggroup)

        logstream = component._resolve_logstream()

        assert isinstance(logstream, LogStream)
        assert logstream.name == "test::stream"

    def test_resolve_logstream_uses_component_format(self):
        """Test resolve logstream uses component's format."""
        custom_format = Mock(spec=FormatLike)
        component = Component(name="test", logformat=custom_format)

        logstream = component._resolve_logstream()

        assert logstream.format is custom_format


class TestComponentLogMethod:
    """Test log method."""

    def test_log_basic_message(self):
        """Test log method with basic message."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.log("Test message")

        component.logstream.log.assert_called_once_with(
            level="INFO",
            message="Test message",
        )

    def test_log_with_kwargs(self):
        """Test log method with additional kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.log("Test message", extra_key="extra_value")

        component.logstream.log.assert_called_once_with(
            level="INFO",
            message="Test message",
            extra_key="extra_value",
        )

    def test_log_uses_info_level(self):
        """Test log method always uses INFO level."""
        component = Component(name="test", level="ERROR")
        component.logstream = Mock(spec=LogStream)

        component.log("Message")

        # Should use INFO level regardless of component level
        args = component.logstream.log.call_args
        assert args.kwargs["level"] == "INFO"


class TestComponentInfoMethod:
    """Test info method."""

    def test_info_basic_message(self):
        """Test info method with basic message."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.info("Info message")

        component.logstream.log.assert_called_once_with(
            level="INFO",
            message="Info message",
        )

    def test_info_with_kwargs(self):
        """Test info method with additional kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.info("Info message", user_id=123)

        component.logstream.log.assert_called_once_with(
            level="INFO",
            message="Info message",
            user_id=123,
        )


class TestComponentErrorMethod:
    """Test error method."""

    def test_error_basic_message(self):
        """Test error method with basic message."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.error("Error message")

        component.logstream.log.assert_called_once_with(
            level="ERROR",
            message="Error message",
        )

    def test_error_with_kwargs(self):
        """Test error method with additional kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.error("Error message", error_code=500)

        component.logstream.log.assert_called_once_with(
            level="ERROR",
            message="Error message",
            error_code=500,
        )


class TestComponentDebugMethod:
    """Test debug method."""

    def test_debug_basic_message(self):
        """Test debug method with basic message."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.debug("Debug message")

        component.logstream.log.assert_called_once_with(
            level="DEBUG",
            message="Debug message",
        )

    def test_debug_with_kwargs(self):
        """Test debug method with additional kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.debug("Debug message", debug_info="details")

        component.logstream.log.assert_called_once_with(
            level="DEBUG",
            message="Debug message",
            debug_info="details",
        )


class TestComponentWarningMethod:
    """Test warning method."""

    def test_warning_basic_message(self):
        """Test warning method with basic message."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.warning("Warning message")

        component.logstream.log.assert_called_once_with(
            level="WARNING",
            message="Warning message",
        )

    def test_warning_with_kwargs(self):
        """Test warning method with additional kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        component.warning("Warning message", severity="medium")

        component.logstream.log.assert_called_once_with(
            level="WARNING",
            message="Warning message",
            severity="medium",
        )


class TestComponentIntegration:
    """Integration tests for Component class."""

    def test_component_lifecycle(self):
        """Test complete component lifecycle."""
        # Create component
        component = Component(
            name="integration-test",
            level="DEBUG",
        )

        # Verify all components are initialized
        assert component.name == "integration-test"
        assert component.level == "DEBUG"
        assert isinstance(component.logstream, LogStream)
        assert component.logstream.name == "integration-test::stream"

    def test_multiple_components_independence(self):
        """Test multiple components don't interfere with each other."""
        component1 = Component(name="component1", level="INFO")
        component2 = Component(name="component2", level="ERROR")

        assert component1.name != component2.name
        assert component1.level != component2.level
        assert component1.logstream is not component2.logstream

    def test_component_with_custom_configuration(self):
        """Test component with custom configuration."""
        custom_format = Mock(spec=FormatLike)
        loggroup = Mock(spec=LogGroup)

        component = Component(
            name="custom",
            level="warning",
            logformat=custom_format,
            loggroup=loggroup,
        )

        assert component.name == "custom"
        assert component.level == "WARNING"
        assert component.logformat is custom_format
        assert component.loggroup is loggroup
        assert isinstance(component.logstream, LogStream)


class TestComponentParentInheritance:
    """Test parent-child component inheritance."""

    def test_child_inherits_parent_name(self):
        """Test child component inherits parent name prefix."""
        parent = Component(name="parent", level="INFO")
        child = Component(parent=parent)

        assert child.name == "parent::Component"
        assert child.parent is parent

    def test_child_inherits_parent_level(self):
        """Test child component inherits parent log level."""
        parent = Component(name="parent", level="ERROR")
        child = Component(name="child", parent=parent)

        assert child.level == "ERROR"

    def test_child_inherits_parent_logformat(self):
        """Test child component inherits parent log format."""
        custom_format = Mock(spec=FormatLike)
        parent = Component(name="parent", logformat=custom_format)
        child = Component(name="child", parent=parent)

        assert child.logformat is custom_format

    def test_child_inherits_parent_loggroup(self):
        """Test child component inherits parent log group."""
        parent_group = Mock(spec=LogGroup)
        parent = Component(name="parent", loggroup=parent_group)
        child = Component(name="child", parent=parent)

        assert child.loggroup is parent_group

    def test_child_can_override_parent_level(self):
        """Test child component can override parent level."""
        parent = Component(name="parent", level="INFO")
        child = Component(name="child", parent=parent, level="DEBUG")

        assert parent.level == "INFO"
        assert child.level == "DEBUG"

    def test_child_can_override_parent_name(self):
        """Test child component can override parent name."""
        parent = Component(name="parent")
        child = Component(name="custom-child", parent=parent)

        assert child.name == "custom-child"

    def test_nested_parent_chain(self):
        """Test deeply nested parent-child chain."""
        grandparent = Component(name="grandparent", level="ERROR")
        parent = Component(name="parent", parent=grandparent)
        child = Component(parent=parent)

        assert grandparent.level == "ERROR"
        assert parent.level == "ERROR"
        assert child.level == "ERROR"
        assert child.name == "parent::Component"


class TestComponentLoggroupBool:
    """Test loggroup boolean auto-creation."""

    def test_loggroup_true_creates_group(self):
        """Test loggroup=True creates a LogGroup automatically."""
        component = Component(name="test", loggroup=True)

        assert component.loggroup is not None
        assert isinstance(component.loggroup, LogGroup)
        assert component.loggroup.name == "test::group"

    def test_loggroup_false_no_group(self):
        """Test loggroup=False creates no group."""
        component = Component(name="test", loggroup=False)

        assert component.loggroup is None

    def test_loggroup_none_no_group(self):
        """Test loggroup=None creates no group."""
        component = Component(name="test", loggroup=None)

        assert component.loggroup is None


class TestComponentDefaultBehavior:
    """Test component default behaviors."""

    def test_default_name_uses_classname(self):
        """Test default name uses class name when not specified."""
        component = Component()

        assert component.name == "Component"

    def test_default_level_is_info(self):
        """Test default log level is INFO."""
        component = Component(name="test")

        assert component.level == "INFO"

    def test_default_logformat_is_text(self):
        """Test default log format is Text."""
        component = Component(name="test")

        assert isinstance(component.logformat, Text)

    def test_default_loggroup_is_none(self):
        """Test default log group is None."""
        component = Component(name="test")

        assert component.loggroup is None

    def test_default_parent_is_none(self):
        """Test default parent is None."""
        component = Component(name="test")

        assert component.parent is None


class TestComponentEdgeCases:
    """Test component edge cases and error conditions."""

    def test_empty_string_name_uses_default(self):
        """Test empty string name uses class name."""
        component = Component(name="")

        assert component.name == "Component"

    def test_empty_string_level_uses_default(self):
        """Test empty string level uses default INFO."""
        component = Component(name="test", level="")

        assert component.level == "INFO"

    def test_level_case_insensitive(self):
        """Test level is case-insensitive."""
        component1 = Component(name="test1", level="debug")
        component2 = Component(name="test2", level="DeBuG")
        component3 = Component(name="test3", level="DEBUG")

        assert component1.level == "DEBUG"
        assert component2.level == "DEBUG"
        assert component3.level == "DEBUG"

    def test_logstream_includes_loggroup_when_present(self):
        """Test logstream includes groups when loggroup is set."""
        component = Component(name="test", loggroup=True)

        assert component.logstream.groups == [component.loggroup]

    def test_logstream_empty_groups_when_no_loggroup(self):
        """Test logstream has empty groups when no loggroup."""
        component = Component(name="test", loggroup=False)

        assert component.logstream.groups == []

    def test_parent_without_expected_attributes(self):
        """Test parent without expected attributes doesn't break."""
        mock_parent = Mock(spec=[])  # Parent without any attributes
        component = Component(name="test", parent=mock_parent)

        # Should use defaults when parent doesn't have expected attributes
        assert component.name == "test"
        assert component.level == "INFO"
        assert isinstance(component.logformat, Text)


class TestComponentSubclassing:
    """Test component subclassing behavior."""

    def test_subclass_default_name_uses_subclass_name(self):
        """Test subclass uses its own class name as default."""

        class CustomComponent(Component):
            pass

        custom = CustomComponent()

        assert custom.name == "CustomComponent"

    def test_subclass_inherits_all_logging_methods(self):
        """Test subclass inherits all logging methods."""

        class CustomComponent(Component):
            pass

        custom = CustomComponent(name="custom")
        custom.logstream = Mock(spec=LogStream)

        # Test all methods are available
        custom.log("test")
        custom.info("test")
        custom.debug("test")
        custom.error("test")
        custom.warning("test")

        assert custom.logstream.log.call_count == 5


class TestComponentGetRoot:
    """Test get_root method."""

    def test_get_root_single_component(self):
        """Test get_root on component without parent returns itself."""
        component = Component(name="root")

        root = component.get_root()

        assert root is component

    def test_get_root_with_parent(self):
        """Test get_root with parent returns parent."""
        parent = Component(name="parent")
        child = Component(name="child", parent=parent)

        root = child.get_root()

        assert root is parent

    def test_get_root_deep_hierarchy(self):
        """Test get_root in deep hierarchy returns top-level parent."""
        grandparent = Component(name="grandparent")
        parent = Component(name="parent", parent=grandparent)
        child = Component(name="child", parent=parent)
        grandchild = Component(name="grandchild", parent=child)

        root = grandchild.get_root()

        assert root is grandparent

    def test_get_root_from_middle_of_hierarchy(self):
        """Test get_root from middle component returns root."""
        root = Component(name="root")
        middle = Component(name="middle", parent=root)
        Component(name="leaf", parent=middle)  # Create hierarchy depth

        root_from_middle = middle.get_root()

        assert root_from_middle is root

    def test_get_root_multiple_branches(self):
        """Test get_root works correctly in branched hierarchy."""
        root = Component(name="root")
        branch1 = Component(name="branch1", parent=root)
        branch2 = Component(name="branch2", parent=root)

        assert branch1.get_root() is root
        assert branch2.get_root() is root


class TestComponentGetDepth:
    """Test get_depth method."""

    def test_get_depth_root_component(self):
        """Test get_depth returns 0 for root component."""
        component = Component(name="root")

        depth = component.get_depth()

        assert depth == 0

    def test_get_depth_direct_child(self):
        """Test get_depth returns 1 for direct child."""
        parent = Component(name="parent")
        child = Component(name="child", parent=parent)

        depth = child.get_depth()

        assert depth == 1

    def test_get_depth_grandchild(self):
        """Test get_depth returns 2 for grandchild."""
        grandparent = Component(name="grandparent")
        parent = Component(name="parent", parent=grandparent)
        child = Component(name="child", parent=parent)

        depth = child.get_depth()

        assert depth == 2

    def test_get_depth_deep_hierarchy(self):
        """Test get_depth with deep hierarchy."""
        components = [Component(name="root")]
        for i in range(1, 5):
            components.append(Component(name=f"level{i}", parent=components[-1]))

        # Verify depths
        for i, component in enumerate(components):
            assert component.get_depth() == i

    def test_get_depth_multiple_siblings(self):
        """Test get_depth with siblings returns same depth."""
        parent = Component(name="parent")
        child1 = Component(name="child1", parent=parent)
        child2 = Component(name="child2", parent=parent)

        assert child1.get_depth() == 1
        assert child2.get_depth() == 1


class TestComponentHierarchyIntegration:
    """Integration tests for component hierarchy features."""

    def test_complex_hierarchy_consistency(self):
        """Test complex hierarchy maintains consistency."""
        root = Component(name="root", level="INFO")
        branch1 = Component(name="branch1", parent=root)
        branch2 = Component(name="branch2", parent=root, level="DEBUG")
        leaf1 = Component(name="leaf1", parent=branch1)
        leaf2 = Component(name="leaf2", parent=branch2)

        # All components should resolve to same root
        assert root.get_root() is root
        assert branch1.get_root() is root
        assert branch2.get_root() is root
        assert leaf1.get_root() is root
        assert leaf2.get_root() is root

        # Depths should be correct
        assert root.get_depth() == 0
        assert branch1.get_depth() == 1
        assert branch2.get_depth() == 1
        assert leaf1.get_depth() == 2
        assert leaf2.get_depth() == 2

        # Level inheritance should work
        assert leaf1.level == "INFO"  # Inherited from root through branch1
        assert leaf2.level == "DEBUG"  # Inherited from branch2

    def test_hierarchy_with_mixed_configurations(self):
        """Test hierarchy with different configurations at each level."""
        custom_format = Mock(spec=FormatLike)
        loggroup = Mock(spec=LogGroup)

        root = Component(name="root", level="ERROR", logformat=custom_format)
        child = Component(name="child", parent=root, loggroup=loggroup)
        grandchild = Component(name="grandchild", parent=child, level="DEBUG")

        # Verify inheritance and overrides
        assert root.level == "ERROR"
        assert child.level == "ERROR"  # Inherited
        assert grandchild.level == "DEBUG"  # Override

        assert root.logformat is custom_format
        assert child.logformat is custom_format  # Inherited
        assert grandchild.logformat is custom_format  # Inherited

        assert root.loggroup is None
        assert child.loggroup is loggroup
        assert grandchild.loggroup is loggroup  # Inherited

        # All should share the same root
        assert grandchild.get_root() is root
        assert grandchild.get_depth() == 2


class TestComponentAdvancedEdgeCases:
    """Test advanced edge cases and boundary conditions."""

    def test_very_deep_hierarchy(self):
        """Test component with very deep hierarchy (100 levels)."""
        components = [Component(name="root")]
        for i in range(1, 100):
            components.append(Component(parent=components[-1]))

        leaf = components[-1]
        assert leaf.get_depth() == 99
        assert leaf.get_root() is components[0]

    def test_multiple_children_same_parent(self):
        """Test multiple children with same parent maintain independence."""
        parent = Component(name="parent", level="INFO")
        children = [Component(name=f"child{i}", parent=parent) for i in range(10)]

        # All children should have same depth and root
        for child in children:
            assert child.get_depth() == 1
            assert child.get_root() is parent
            assert child.level == "INFO"

        # Children should be independent
        for i, child in enumerate(children):
            assert child.name == f"child{i}"

    def test_sibling_with_different_configs_do_not_affect_each_other(self):
        """Test siblings with different configs are independent."""
        parent = Component(name="parent")
        child1 = Component(name="child1", parent=parent, level="DEBUG", loggroup=True)
        child2 = Component(name="child2", parent=parent, level="ERROR", loggroup=False)

        assert child1.level == "DEBUG"
        assert child2.level == "ERROR"
        assert child1.loggroup is not None
        assert child2.loggroup is None
        assert child1.logstream is not child2.logstream

    def test_name_with_special_characters(self):
        """Test component name with special characters."""
        special_names = [
            "component-with-dashes",
            "component_with_underscores",
            "component.with.dots",
            "component::with::colons",
            "component/with/slashes",
        ]

        for name in special_names:
            component = Component(name=name)
            assert component.name == name

    def test_mixed_case_level_normalization(self):
        """Test various case combinations for log level."""
        test_cases = [
            ("info", "INFO"),
            ("Info", "INFO"),
            ("INFO", "INFO"),
            ("debug", "DEBUG"),
            ("DeBuG", "DEBUG"),
            ("warning", "WARNING"),
            ("WaRnInG", "WARNING"),
            ("error", "ERROR"),
            ("ErRoR", "ERROR"),
        ]

        for input_level, expected in test_cases:
            component = Component(name="test", level=input_level)
            assert component.level == expected

    def test_loggroup_auto_naming(self):
        """Test automatic log group naming."""
        component = Component(name="my-component", loggroup=True)

        assert component.loggroup is not None
        assert component.loggroup.name == "my-component::group"

    def test_logstream_naming_convention(self):
        """Test log stream follows naming convention."""
        component = Component(name="test-component")

        assert component.logstream.name == "test-component::stream"

    def test_parent_child_name_composition(self):
        """Test name composition in parent-child relationships."""
        parent = Component(name="parent")
        child_default = Component(parent=parent)
        child_explicit = Component(name="explicit", parent=parent)

        assert child_default.name == "parent::Component"
        assert child_explicit.name == "explicit"

    def test_inheritance_chain_integrity(self):
        """Test inheritance chain maintains integrity throughout."""
        custom_format = Mock(spec=FormatLike)

        level1 = Component(name="level1", level="ERROR", logformat=custom_format)
        level2 = Component(parent=level1)
        level3 = Component(parent=level2)
        level4 = Component(parent=level3, level="DEBUG")

        # Check level inheritance and override
        assert level1.level == "ERROR"
        assert level2.level == "ERROR"
        assert level3.level == "ERROR"
        assert level4.level == "DEBUG"

        # Check format inheritance
        assert level1.logformat is custom_format
        assert level2.logformat is custom_format
        assert level3.logformat is custom_format
        assert level4.logformat is custom_format

        # Check hierarchy methods
        assert level4.get_root() is level1
        assert level4.get_depth() == 3

    def test_component_with_none_values(self):
        """Test component handles None values gracefully."""
        component = Component(
            name=None,
            level=None,
            parent=None,
            logformat=None,
            loggroup=None,
        )

        assert component.name == "Component"
        assert component.level == "INFO"
        assert isinstance(component.logformat, Text)
        assert component.loggroup is None
        assert component.parent is None

    def test_log_methods_preserve_kwargs_order(self):
        """Test that log methods preserve kwargs."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        test_kwargs = {"key1": "value1", "key2": 123, "key3": True, "key4": None}
        component.info("test message", **test_kwargs)

        call_kwargs = component.logstream.log.call_args.kwargs
        assert call_kwargs["level"] == "INFO"
        assert call_kwargs["message"] == "test message"
        for key, value in test_kwargs.items():
            assert call_kwargs[key] == value

    def test_all_log_methods_use_correct_levels(self):
        """Test all log methods use their designated levels."""
        component = Component(name="test")
        component.logstream = Mock(spec=LogStream)

        test_methods = [
            (component.log, "INFO"),
            (component.info, "INFO"),
            (component.debug, "DEBUG"),
            (component.warning, "WARNING"),
            (component.error, "ERROR"),
        ]

        for method, expected_level in test_methods:
            component.logstream.reset_mock()
            method("test message")
            assert component.logstream.log.call_args.kwargs["level"] == expected_level
