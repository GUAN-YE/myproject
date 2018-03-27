<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="jingquechazhao.aspx.cs" Inherits="jingquechazhao" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
<div align="center" 
        style="background-image: url('背景图/46b6ed20645eb62030fbd1a504863869.jpg')">
    <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
         >
        <Columns>
            <asp:TemplateField HeaderText="照片">
                <ItemTemplate>
                    <asp:Image ID="Image2" runat="server" Height="255px" 
                        ImageUrl='<%# Eval("tupian") %>' Width="215px" />
                </ItemTemplate>
            </asp:TemplateField>
            <asp:BoundField DataField="pinpai" HeaderText="品牌" />
            <asp:HyperLinkField DataNavigateUrlFields="xinghao" 
                DataNavigateUrlFormatString="xiangqing.aspx?id={0}" DataTextField="xinghao" 
                HeaderText="型号" />
            <asp:BoundField DataField="jiage" HeaderText="价格" />
            <asp:BoundField DataField="xiaoliang" HeaderText="销量" />
            <asp:BoundField DataField="kucun" HeaderText="库存" />
        </Columns>
        <EmptyDataTemplate>
            <asp:Image ID="Image1" runat="server" ImageUrl='<%# Eval("tupian") %>' />
        </EmptyDataTemplate>
    </asp:GridView>
    </div>
</asp:Content>

